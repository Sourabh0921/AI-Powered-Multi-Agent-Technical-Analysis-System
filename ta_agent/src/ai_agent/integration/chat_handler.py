"""
Chat Handler Module
Manages conversational interface with memory
"""
from typing import Dict, Any, Optional, List
import pandas as pd

from ...core.logging import logger


class ChatHandler:
    """
    Handles conversational interactions with memory
    
    Features:
    - Conversation history management
    - Context building from history
    - Multi-turn conversations
    """
    
    def __init__(self, max_history: int = 10):
        """
        Initialize chat handler
        
        Args:
            max_history: Maximum number of messages to keep in history
        """
        self.max_history = max_history
    
    def process_message(
        self,
        message: str,
        response: Dict[str, Any],
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message and update conversation history
        
        Args:
            message: User message
            response: System response (from query or analysis)
            conversation_history: Previous conversation history
            
        Returns:
            Response with updated conversation history
        """
        logger.info("💬 Processing chat message...")
        
        # Initialize or get existing history
        history = conversation_history or []
        
        # Add user message
        history.append({
            "role": "user",
            "content": message,
            "timestamp": pd.Timestamp.now().isoformat()
        })
        
        # Add assistant response
        assistant_content = response.get("integrated_answer", response.get("answer", ""))
        history.append({
            "role": "assistant",
            "content": assistant_content,
            "timestamp": pd.Timestamp.now().isoformat()
        })
        
        # Trim history if too long
        if len(history) > self.max_history * 2:  # *2 because each exchange is 2 messages
            history = history[-(self.max_history * 2):]
        
        # Add history to response
        response["conversation_history"] = history
        
        return response
    
    def build_context_from_history(
        self,
        conversation_history: List[Dict],
        max_messages: int = 5
    ) -> str:
        """
        Build context string from conversation history
        
        Args:
            conversation_history: List of conversation messages
            max_messages: Maximum number of recent messages to include
            
        Returns:
            Formatted context string
        """
        if not conversation_history:
            return ""
        
        # Get recent messages
        recent_messages = conversation_history[-(max_messages * 2):]
        
        # Format as context
        context_parts = ["Previous conversation:"]
        for msg in recent_messages:
            role = msg["role"].capitalize()
            content = msg["content"][:200]  # Limit length
            context_parts.append(f"{role}: {content}...")
        
        return "\n".join(context_parts)
    
    def get_conversation_summary(
        self,
        conversation_history: List[Dict]
    ) -> Dict[str, Any]:
        """
        Generate summary of conversation
        
        Args:
            conversation_history: Complete conversation history
            
        Returns:
            Conversation statistics and summary
        """
        if not conversation_history:
            return {
                "total_messages": 0,
                "user_messages": 0,
                "assistant_messages": 0,
                "topics": []
            }
        
        user_messages = [m for m in conversation_history if m["role"] == "user"]
        assistant_messages = [m for m in conversation_history if m["role"] == "assistant"]
        
        # Extract topics (simple heuristic - look for tickers and keywords)
        topics = set()
        keywords = ["analysis", "price", "recommendation", "risk", "buy", "sell"]
        
        for msg in user_messages:
            content = msg["content"].lower()
            # Extract potential tickers (simple pattern)
            words = content.split()
            for word in words:
                if word.isupper() and 2 <= len(word) <= 5:
                    topics.add(word)
                elif any(kw in word for kw in keywords):
                    topics.add(word)
        
        return {
            "total_messages": len(conversation_history),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "topics": list(topics)[:5],  # Top 5 topics
            "start_time": conversation_history[0].get("timestamp") if conversation_history else None,
            "last_time": conversation_history[-1].get("timestamp") if conversation_history else None
        }
    
    def clear_history(self) -> Dict[str, str]:
        """
        Clear conversation history
        
        Returns:
            Confirmation message
        """
        return {
            "status": "success",
            "message": "Conversation history cleared"
        }
    
    def export_conversation(
        self,
        conversation_history: List[Dict],
        format: str = "json"
    ) -> Any:
        """
        Export conversation history
        
        Args:
            conversation_history: Conversation to export
            format: Export format (json, text)
            
        Returns:
            Exported conversation in specified format
        """
        if format == "json":
            return conversation_history
        
        elif format == "text":
            lines = []
            for msg in conversation_history:
                role = msg["role"].capitalize()
                content = msg["content"]
                timestamp = msg.get("timestamp", "")
                lines.append(f"[{timestamp}] {role}: {content}\n")
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
