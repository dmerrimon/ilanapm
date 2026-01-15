"""
Tests for ML Advisory Module

Tests duration prediction and risk scoring functionality.
"""

import pytest
from backend.models.timeline import (
    Timeline, Task, Dependency,
    StudyPhase, RegulatoryAuthority, TaskCategory
)
from backend.ml_advisory import DurationPredictor, RiskScorer
from backend.config import load_config


# Test configuration
TEST_CONFIG = load_config()


class TestDurationPredictor:
    """Test suite for duration predictor"""
    
    def test_predict_known_task(self):
        """Test prediction for known task type"""
        task = Task(
            id="T1",
            name="IND/CTA Submission",
            duration_days=45,
            category=TaskCategory.REGULATORY,
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            is_mandatory=True
        )
        
        predictor = DurationPredictor(TEST_CONFIG)
        prediction = predictor.predict_duration(task)
        
        # Should have prediction
        assert 'predicted_duration_days' in prediction
        assert 'confidence_interval' in prediction
        assert 'confidence_score' in prediction
        assert 'explanation' in prediction
        
        # Confidence should be high for known task
        assert prediction['confidence_score'] > 0.7
        
        # Should have bounds
        assert prediction['confidence_interval']['lower'] < prediction['predicted_duration_days']
        assert prediction['confidence_interval']['upper'] > prediction['predicted_duration_days']
    
    def test_predict_unknown_task(self):
        """Test prediction for unknown task type"""
        task = Task(
            id="T1",
            name="Unknown Novel Task",
            duration_days=30,
            category=TaskCategory.OPERATIONAL,
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA
        )
        
        predictor = DurationPredictor(TEST_CONFIG)
        prediction = predictor.predict_duration(task)
        
        # Should still return prediction
        assert 'predicted_duration_days' in prediction
        
        # Confidence should be lower for unknown task
        assert prediction['confidence_score'] < 0.6
        
        # Should use task's duration as default
        assert prediction['predicted_duration_days'] == task.duration_days
    
    def test_predict_with_authority_adjustment(self):
        """Test that authority-specific adjustments are applied"""
        task = Task(
            id="T1",
            name="IRB Approval",
            duration_days=45,
            category=TaskCategory.REGULATORY,
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA
        )
        
        predictor = DurationPredictor(TEST_CONFIG)
        prediction = predictor.predict_duration(task)
        
        # Should have reasonable prediction
        assert prediction['predicted_duration_days'] > 0
        assert prediction['confidence_score'] > 0
    
    def test_predict_timeline_durations(self):
        """Test prediction for multiple tasks"""
        tasks = [
            Task(
                id="T1",
                name="Task 1",
                duration_days=30,
                category=TaskCategory.REGULATORY,
                phase=StudyPhase.PHASE_II,
                authority=RegulatoryAuthority.FDA
            ),
            Task(
                id="T2",
                name="Task 2",
                duration_days=45,
                category=TaskCategory.OPERATIONAL,
                phase=StudyPhase.PHASE_II,
                authority=RegulatoryAuthority.FDA
            ),
        ]
        
        predictor = DurationPredictor(TEST_CONFIG)
        result = predictor.predict_timeline_durations(tasks)
        
        assert 'predictions' in result
        assert 'average_confidence' in result
        assert 'total_tasks' in result
        assert len(result['predictions']) == 2
        assert result['total_tasks'] == 2


class TestRiskScorer:
    """Test suite for risk scorer"""
    
    def test_score_low_risk_task(self):
        """Test scoring for low risk task"""
        task = Task(
            id="T1",
            name="Documentation Review",
            duration_days=10,
            category=TaskCategory.OPERATIONAL,
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            is_mandatory=False,
            checklist_completion_pct=100
        )
        
        scorer = RiskScorer(TEST_CONFIG)
        risk = scorer.score_risk(task)
        
        assert 'risk_score' in risk
        assert 'risk_level' in risk
        assert 'risk_factors' in risk
        assert 'mitigation_suggestions' in risk
        
        # Should be low risk
        assert risk['risk_level'] in ['low', 'medium']
        assert risk['risk_score'] < 50
    
    def test_score_high_risk_task(self):
        """Test scoring for high risk task"""
        task = Task(
            id="T1",
            name="IND/CTA Submission",
            duration_days=20,  # Very aggressive!
            category=TaskCategory.REGULATORY,
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            is_mandatory=True,
            checklist_completion_pct=30  # Incomplete!
        )
        
        scorer = RiskScorer(TEST_CONFIG)
        risk = scorer.score_risk(task)
        
        # Should be high risk
        assert risk['risk_score'] > 50
        assert risk['risk_level'] in ['high', 'critical']
        assert len(risk['risk_factors']) > 0
        assert len(risk['mitigation_suggestions']) > 0
    
    def test_score_with_context(self):
        """Test scoring with timeline context"""
        task = Task(
            id="T1",
            name="Task 1",
            duration_days=30,
            category=TaskCategory.REGULATORY,
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            is_mandatory=True
        )
        
        context = {
            "on_critical_path": True,
            "total_tasks": 10
        }
        
        scorer = RiskScorer(TEST_CONFIG)
        risk = scorer.score_risk(task, context)
        
        # Should have additional risk from being on critical path
        assert any('critical path' in f.lower() for f in risk['risk_factors'])
    
    def test_score_timeline_risks(self):
        """Test scoring for entire timeline"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="IND/CTA Submission",
                    duration_days=20,
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA,
                    is_mandatory=True,
                    checklist_completion_pct=30
                ),
                Task(
                    id="T2",
                    name="IRB Approval",
                    duration_days=45,
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA,
                    is_mandatory=True
                ),
            ],
            dependencies=[
                Dependency(predecessor_id="T1", successor_id="T2")
            ]
        )
        
        scorer = RiskScorer(TEST_CONFIG)
        result = scorer.score_timeline_risks(timeline)
        
        assert 'risk_scores' in result
        assert 'high_risk_tasks' in result
        assert 'average_risk' in result
        assert len(result['risk_scores']) == 2
        
        # T1 should be high risk (aggressive duration + low checklist)
        assert len(result['high_risk_tasks']) >= 1
    
    def test_regulatory_task_risk_factors(self):
        """Test that regulatory tasks get appropriate risk factors"""
        task = Task(
            id="T1",
            name="Ethics Committee Approval",
            duration_days=45,
            category=TaskCategory.REGULATORY,
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            is_mandatory=True
        )
        
        scorer = RiskScorer(TEST_CONFIG)
        risk = scorer.score_risk(task)
        
        # Should have regulatory-specific factors
        assert risk['risk_score'] > 0
        
        # Should have regulatory-specific mitigations
        mitigations_text = ' '.join(risk['mitigation_suggestions']).lower()
        assert 'regulatory' in mitigations_text or 'consultant' in mitigations_text
    
    def test_mandatory_task_impact(self):
        """Test that mandatory tasks increase risk"""
        task_optional = Task(
            id="T1",
            name="Task",
            duration_days=30,
            category=TaskCategory.OPERATIONAL,
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            is_mandatory=False
        )
        
        task_mandatory = Task(
            id="T2",
            name="Task",
            duration_days=30,
            category=TaskCategory.OPERATIONAL,
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            is_mandatory=True
        )
        
        scorer = RiskScorer(TEST_CONFIG)
        risk_optional = scorer.score_risk(task_optional)
        risk_mandatory = scorer.score_risk(task_mandatory)
        
        # Mandatory task should have higher risk
        assert risk_mandatory['risk_score'] >= risk_optional['risk_score']
    
    def test_checklist_completion_impact(self):
        """Test that incomplete checklist increases risk"""
        task_complete = Task(
            id="T1",
            name="Task",
            duration_days=30,
            category=TaskCategory.REGULATORY,
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            checklist_completion_pct=100
        )
        
        task_incomplete = Task(
            id="T2",
            name="Task",
            duration_days=30,
            category=TaskCategory.REGULATORY,
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            checklist_completion_pct=30
        )
        
        scorer = RiskScorer(TEST_CONFIG)
        risk_complete = scorer.score_risk(task_complete)
        risk_incomplete = scorer.score_risk(task_incomplete)
        
        # Incomplete checklist should have higher risk
        assert risk_incomplete['risk_score'] > risk_complete['risk_score']


class TestMLAdvisoryIntegration:
    """Integration tests for ML advisory services"""
    
    def test_duration_and_risk_together(self):
        """Test that duration prediction and risk scoring work together"""
        task = Task(
            id="T1",
            name="IND/CTA Submission",
            duration_days=45,
            category=TaskCategory.REGULATORY,
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            is_mandatory=True,
            checklist_completion_pct=50
        )
        
        predictor = DurationPredictor(TEST_CONFIG)
        scorer = RiskScorer(TEST_CONFIG)
        
        duration = predictor.predict_duration(task)
        risk = scorer.score_risk(task)
        
        # Both should return valid results
        assert duration['confidence_score'] > 0
        assert risk['risk_score'] >= 0
        
        # If duration is aggressive, risk should reflect that
        if task.duration_days < duration['confidence_interval']['lower']:
            assert risk['risk_score'] > 30


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
