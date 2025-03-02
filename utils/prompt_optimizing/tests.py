import pytest

from utils.prompt_optimizing.optimizer import _extract_prompt_from_response, _extract_score_from_response, \
    _create_evaluation_prompt_for_single_criterion, PromptOptimizer


# Test 1: Extracting prompt from XML tags
def test_extract_prompt_with_tags():
    """Test we can extract text between <PROMPT> tags"""
    text = "<PROMPT>Write about dogs</PROMPT> some extra text"
    result = _extract_prompt_from_response(text)
    assert result == "Write about dogs"


# Test 2: Handling text without tags
def test_extract_prompt_without_tags():
    """Test we get clean text when there's no tags"""
    text = "   Write about cats   "
    result = _extract_prompt_from_response(text)
    assert result == "Write about cats"


# Test 3: Normal score extraction
def test_extract_valid_score():
    """Test we can find numbers in text"""
    text = "Score: 8.5/10"
    result = _extract_score_from_response(text)
    assert result == 8.5


# Test 4: Score clamping at maximum
def test_extract_score_above_10():
    """Test scores can't go above 10"""
    text = "15.9 points"
    result = _extract_score_from_response(text)
    assert result == 10.0


# Test 5: Score clamping at minimum
def test_extract_score_below_0():
    """Test scores can't go below 0"""
    text = "-5.3"
    result = _extract_score_from_response(text)
    assert result == 0.0


# Test 6: Evaluation prompt creation
def test_create_evaluation_prompt():
    """Test evaluation prompt includes all important information"""
    criterion = {
        'name': 'Creativity',
        'description': 'Original ideas'
    }
    response = "AI response"
    prompt = "Original prompt"

    result = _create_evaluation_prompt_for_single_criterion(criterion, response, prompt)

    assert 'Creativity' in result
    assert 'Original ideas' in result
    assert 'AI response' in result
    assert 'Original prompt' in result


# Test 7: Optimizer initialization
def test_optimizer_initialization():
    """Test optimizer stores settings correctly"""
    criteria = [{'name': 'Test', 'description': 'Test'}]
    optimizer = PromptOptimizer(api_key="123", criteria=criteria)

    assert optimizer.max_iterations == 5
    assert optimizer.score_threshold == 8.0
    assert len(optimizer.criteria) == 1


# Test 8: Criteria formatting
def test_format_criteria():
    """Test criteria are shown with names and weights"""
    criteria = [{
        'name': 'Quality',
        'description': 'High standard',
        'weight': 2.0
    }]
    optimizer = PromptOptimizer(api_key="123", criteria=criteria)

    formatted = optimizer._format_criteria_for_feedback()

    assert "Quality" in formatted
    assert "High standard" in formatted
    assert "weight 2.0" in formatted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
