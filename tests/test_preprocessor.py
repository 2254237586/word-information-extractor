from src.text_preprocessor import clean_text, split_sentences


def test_clean_and_split():
    result = split_sentences([{"paragraph_id": 2, "text": "明天  下午开会! 天气不错。"}])
    assert clean_text("a   b!") == "a b！"
    assert [x["text"] for x in result] == ["明天 下午开会", "天气不错"]
    assert result[0]["paragraph_id"] == 2

