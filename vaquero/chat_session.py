"""Chat session management for conversational AI applications."""

import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ChatSession:
    """Manages chat session state and lifecycle for conversational AI applications."""

    def __init__(
        self,
        session_id: str,
        name: Optional[str] = None,
        session_type: str = "chat",
        timeout_minutes: int = 30,
        max_duration_minutes: int = 240,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize a chat session.

        Args:
            session_id: Unique identifier for the session
            name: Human-readable name for the session
            session_type: Type of session ('chat', 'pipeline', 'workflow')
            timeout_minutes: Minutes of inactivity before session timeout
            max_duration_minutes: Maximum session duration in minutes
            metadata: Additional session metadata
        """
        self.session_id = session_id
        self.name = name or f"chat_session_{session_id}"
        self.session_type = session_type
        self.timeout_minutes = timeout_minutes
        self.max_duration_minutes = max_duration_minutes
        self.metadata = metadata or {}

        # Timing information
        self.start_time = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.end_time: Optional[datetime] = None

        # Session metrics
        self.message_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0

        # Status
        self.status = "active"  # 'active', 'timeout', 'ended', 'cancelled'
        
        # Callback mechanism for timeout events
        self._timeout_callbacks = []

        logger.info(f"Created chat session {self.session_id} of type {self.session_type}")

    def update_activity(self) -> None:
        """Update the last activity timestamp."""
        self.last_activity = datetime.utcnow()
        logger.debug(f"Updated activity for session {self.session_id}")

    def add_message(self, tokens: int = 0, cost: float = 0.0) -> None:
        """Record a new message in the session.

        Args:
            tokens: Number of tokens used in the message
            cost: Cost of the message processing
        """
        self.message_count += 1
        self.total_tokens += tokens
        self.total_cost += cost
        self.update_activity()
        logger.debug(f"Added message to session {self.session_id}: tokens={tokens}, cost={cost}")

    def _register_timeout_callback(self, callback) -> None:
        """Register a callback to be called when session times out.
        
        Args:
            callback: Callable that takes the session as argument
        """
        if callback not in self._timeout_callbacks:
            self._timeout_callbacks.append(callback)
            logger.debug(f"Registered timeout callback for session {self.session_id}")

    def _unregister_timeout_callback(self, callback) -> None:
        """Unregister a timeout callback.
        
        Args:
            callback: Callable to unregister
        """
        if callback in self._timeout_callbacks:
            self._timeout_callbacks.remove(callback)
            logger.debug(f"Unregistered timeout callback for session {self.session_id}")

    def _notify_timeout_callbacks(self) -> None:
        """Notify all registered timeout callbacks."""
        for callback in self._timeout_callbacks:
            try:
                callback(self)
            except Exception as e:
                logger.error(f"Error in timeout callback for session {self.session_id}: {e}")

    def should_end_session(self) -> bool:
        """Check if the session should end due to timeout or max duration.

        Returns:
            True if session should end, False otherwise
        """
        now = datetime.utcnow()
        time_since_activity = now - self.last_activity
        session_duration = now - self.start_time

        timeout_reached = time_since_activity > timedelta(minutes=self.timeout_minutes)
        max_duration_reached = session_duration > timedelta(minutes=self.max_duration_minutes)

        if timeout_reached:
            self.status = "timeout"
            logger.info(f"Session {self.session_id} ended due to timeout")
            # Notify timeout callbacks
            self._notify_timeout_callbacks()
            return True

        if max_duration_reached:
            self.status = "ended"
            logger.info(f"Session {self.session_id} ended due to max duration")
            # Notify timeout callbacks
            self._notify_timeout_callbacks()
            return True

        return False

    def end_session(self, reason: str = "ended") -> None:
        """End the session with a specific reason.

        Args:
            reason: Reason for ending the session
        """
        self.end_time = datetime.utcnow()
        self.status = reason
        logger.info(f"Session {self.session_id} ended with reason: {reason}")

    def get_session_duration_minutes(self) -> float:
        """Get the current session duration in minutes."""
        end_time = self.end_time or datetime.utcnow()
        duration = end_time - self.start_time
        return duration.total_seconds() / 60

    def get_time_to_timeout_minutes(self) -> float:
        """Get minutes until session timeout."""
        now = datetime.utcnow()
        time_since_activity = now - self.last_activity
        time_to_timeout = timedelta(minutes=self.timeout_minutes) - time_since_activity
        return max(0, time_to_timeout.total_seconds() / 60)

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for API payload."""
        return {
            "session_id": self.session_id,
            "name": self.name,
            "session_type": self.session_type,
            "status": self.status,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "last_activity": self.last_activity.isoformat(),
            "timeout_minutes": self.timeout_minutes,
            "max_duration_minutes": self.max_duration_minutes,
            "message_count": self.message_count,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "metadata": self.metadata
        }

    def to_database_dict(self) -> Dict[str, Any]:
        """Convert session to database insert/update format."""
        data = self.to_dict()
        # Add computed fields for database
        data.update({
            "duration_minutes": self.get_session_duration_minutes(),
            "time_to_timeout_minutes": self.get_time_to_timeout_minutes()
        })
        return data

    def __repr__(self) -> str:
        return f"<ChatSession(id='{self.session_id}', type='{self.session_type}', status='{self.status}', messages={self.message_count})>"


class ChatSessionManager:
    """Manages multiple chat sessions and provides session lifecycle utilities."""

    def __init__(self):
        """Initialize the session manager."""
        self.sessions: Dict[str, ChatSession] = {}
        self.logger = logging.getLogger(__name__)

    def create_session(
        self,
        name: Optional[str] = None,
        session_type: str = "chat",
        timeout_minutes: int = 30,
        max_duration_minutes: int = 240,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatSession:
        """Create a new chat session.

        Args:
            name: Human-readable name for the session
            session_type: Type of session
            timeout_minutes: Session timeout in minutes
            max_duration_minutes: Maximum session duration in minutes
            metadata: Additional session metadata

        Returns:
            The created ChatSession instance
        """
        session_id = str(uuid.uuid4())
        session = ChatSession(
            session_id=session_id,
            name=name,
            session_type=session_type,
            timeout_minutes=timeout_minutes,
            max_duration_minutes=max_duration_minutes,
            metadata=metadata
        )

        self.sessions[session_id] = session
        self.logger.info(f"Created new chat session: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a session by ID.

        Args:
            session_id: The session identifier

        Returns:
            ChatSession instance or None if not found
        """
        return self.sessions.get(session_id)

    def end_session(self, session_id: str, reason: str = "ended") -> bool:
        """End a session.

        Args:
            session_id: The session identifier
            reason: Reason for ending the session

        Returns:
            True if session was ended, False if not found
        """
        session = self.sessions.get(session_id)
        if session:
            session.end_session(reason)
            self.logger.info(f"Ended session {session_id} with reason: {reason}")
            return True
        return False

    def cleanup_expired_sessions(self) -> int:
        """Clean up sessions that have timed out or exceeded max duration.

        Returns:
            Number of sessions cleaned up
        """
        expired_sessions = []
        for session_id, session in self.sessions.items():
            if session.should_end_session():
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            session = self.sessions.pop(session_id)
            session.end_session("timeout")
            self.logger.info(f"Cleaned up expired session: {session_id}")

        return len(expired_sessions)

    def get_active_sessions(self) -> Dict[str, ChatSession]:
        """Get all active sessions.

        Returns:
            Dictionary of active sessions by session_id
        """
        return {
            session_id: session
            for session_id, session in self.sessions.items()
            if session.status == "active"
        }

    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about all sessions.

        Returns:
            Dictionary with session statistics
        """
        all_sessions = list(self.sessions.values())
        active_sessions = [s for s in all_sessions if s.status == "active"]

        return {
            "total_sessions": len(all_sessions),
            "active_sessions": len(active_sessions),
            "expired_sessions": len(all_sessions) - len(active_sessions),
            "total_messages": sum(s.message_count for s in all_sessions),
            "total_tokens": sum(s.total_tokens for s in all_sessions),
            "total_cost": sum(s.total_cost for s in all_sessions)
        }


# Global session manager instance
_session_manager = ChatSessionManager()


def get_session_manager() -> ChatSessionManager:
    """Get the global session manager instance."""
    return _session_manager


def create_chat_session(
    name: Optional[str] = None,
    session_type: str = "chat",
    timeout_minutes: int = 30,
    max_duration_minutes: int = 240,
    metadata: Optional[Dict[str, Any]] = None
) -> ChatSession:
    """Convenience function to create a new chat session.

    Args:
        name: Human-readable name for the session
        session_type: Type of session
        timeout_minutes: Session timeout in minutes
        max_duration_minutes: Maximum session duration in minutes
        metadata: Additional session metadata

    Returns:
        The created ChatSession instance
    """
    return _session_manager.create_session(
        name=name,
        session_type=session_type,
        timeout_minutes=timeout_minutes,
        max_duration_minutes=max_duration_minutes,
        metadata=metadata
    )
