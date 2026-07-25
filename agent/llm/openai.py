"""OpenAI 프로바이더 (나중).

/v1/chat/completions, Bearer 인증. 응답 모양이 Claude와 다름:
choices[0].message.content. base.py 규약을 지켜 겉모습만 통일한다.
채우는 시점: 멀티프로바이더 확장 (D4).
"""
