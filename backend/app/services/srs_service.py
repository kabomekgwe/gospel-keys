"""
Spaced Repetition System (SRS) Service

Implements the SuperMemo-2 (SM-2) algorithm for adaptive practice scheduling.
"""

from datetime import datetime, timedelta
from typing import Tuple

class SRSService:
    """
    Service for calculating review schedules using SM-2 algorithm.
    """
    
    @staticmethod
    def calculate_next_review(
        quality: int,
        prev_interval: float,
        prev_ease_factor: float,
        repetition_count: int
    ) -> Tuple[float, float, int]:
        """
        Calculate next review interval using SM-2.
        
        Args:
            quality: 0-5 rating (0=complete blackout, 5=perfect)
            prev_interval: Previous interval in days
            prev_ease_factor: Previous ease factor (min 1.3)
            repetition_count: Number of successful repetitions
            
        Returns:
            Tuple[float, float, int]: (new_interval, new_ease_factor, new_repetition_count)
        """
        
        # 1. Update Repetition Count
        if quality >= 3:
            new_repetition_count = repetition_count + 1
        else:
            new_repetition_count = 0  # Reset on failure
            
        # 2. Update Ease Factor (EF)
        # EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
        if quality >= 3:
            ef_modifier = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
            new_ease_factor = max(1.3, prev_ease_factor + ef_modifier)
        else:
            new_ease_factor = prev_ease_factor  # Don't change EF on failure, or could decrease
            
        # 3. Calculate Interval (I)
        if quality < 3:
            new_interval = 1.0  # Reset to 1 day
        else:
            if new_repetition_count == 1:
                new_interval = 1.0
            elif new_repetition_count == 2:
                new_interval = 6.0
            else:
                new_interval = prev_interval * new_ease_factor
                
        return new_interval, new_ease_factor, new_repetition_count

    @staticmethod
    def get_review_schedule(
        quality: int,
        snippet
    ) -> dict:
        """
        Apply SM-2 to a snippet and return fields to update.
        """
        new_interval, new_ef, new_reps = SRSService.calculate_next_review(
            quality=quality,
            prev_interval=snippet.interval_days,
            prev_ease_factor=snippet.ease_factor,
            repetition_count=snippet.repetition_count
        )
        
        now = datetime.now()
        next_review = now + timedelta(days=new_interval)
        
        return {
            "last_reviewed_at": now,
            "next_review_at": next_review,
            "interval_days": new_interval,
            "ease_factor": new_ef,
            "repetition_count": new_reps
        }
