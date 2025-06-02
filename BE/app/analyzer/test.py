from analyzer import Analyzer

if __name__ == "__main__":
    sample_text = "이거 진짜 달고 맛있어요. 포장도 예쁘고 다시 사먹고 싶어요. 근데 가격은 좀 비싼 편이에요."

    analyzer = Analyzer()
    result = analyzer.run(sample_text)

    from pprint import pprint
    pprint(result)