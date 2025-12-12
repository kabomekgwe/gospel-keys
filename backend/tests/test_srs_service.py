
import pytest
from datetime import datetime, timedelta
from app.services.srs_service import SRSService
from unittest.mock import Mock

class TestSRSService:
    
    def test_calculate_next_review_initial_success(self):
        """Test first successful review."""
        # Quality 4 (Good), first rep
        new_interval, new_ef, new_reps = SRSService.calculate_next_review(
            quality=4,
            prev_interval=0,
            prev_ease_factor=2.5,
            repetition_count=0
        )
        
        assert new_reps == 1
        assert new_interval == 1.0
        assert new_ef == 2.5 # EF doesn't change much on first tries usually, but let's check formula 
        # EF' = 2.5 + (0.1 - (1) * (0.08 + 1 * 0.02)) = 2.5 + (0.1 - 0.1) = 2.5

    def test_calculate_next_review_second_repetition(self):
        """Test second successful review (interval should be 6)."""
        new_interval, new_ef, new_reps = SRSService.calculate_next_review(
            quality=4,
            prev_interval=1.0,
            prev_ease_factor=2.5,
            repetition_count=1
        )
        
        assert new_reps == 2
        assert new_interval == 6.0

    def test_calculate_next_review_growth(self):
        """Test subsequent review with growth."""
        # Rep 2 -> 3
        new_interval, new_ef, new_reps = SRSService.calculate_next_review(
            quality=4,
            prev_interval=6.0,
            prev_ease_factor=2.5,
            repetition_count=2
        )
        
        assert new_reps == 3
        assert new_interval == 6.0 * 2.5  # 15.0 days

    def test_calculate_next_review_failure(self):
        """Test failed review resets interval."""
        new_interval, new_ef, new_reps = SRSService.calculate_next_review(
            quality=1,
            prev_interval=15.0,
            prev_ease_factor=2.6,
            repetition_count=3
        )
        
        assert new_reps == 0
        assert new_interval == 1.0
        assert new_ef == 2.6  # EF should not change on failure

    def test_ease_factor_change(self):
        """Test that ease factor changes based on quality."""
        # Quality 5 (Easy) -> EF increases
        _, ef_easy, _ = SRSService.calculate_next_review(5, 10, 2.5, 2)
        assert ef_easy > 2.5
        
        # Quality 3 (Hard) -> EF decreases
        _, ef_hard, _ = SRSService.calculate_next_review(3, 10, 2.5, 2)
        assert ef_hard < 2.5
        
        # Min EF check
        _, ef_min, _ = SRSService.calculate_next_review(3, 10, 1.3, 2)
        assert ef_min == 1.3

    def test_get_review_schedule(self):
        """Test full schedule generation with dates."""
        mock_snippet = Mock()
        mock_snippet.interval_days = 6.0
        mock_snippet.ease_factor = 2.5
        mock_snippet.repetition_count = 2
        
        result = SRSService.get_review_schedule(4, mock_snippet)
        
        assert "last_reviewed_at" in result
        assert "next_review_at" in result
        assert "interval_days" in result
        
        # Check logic for next interval (6 * 2.5 = 15)
        assert result["interval_days"] == 15.0
        
        # Check date calculation (approximate)
        now = datetime.now()
        expected_next = now + timedelta(days=15)
        # Allow delta of a few seconds/minutes
        assert abs((result["next_review_at"] - expected_next).total_seconds()) < 60
