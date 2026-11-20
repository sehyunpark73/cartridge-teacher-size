# cartridge teacher size

## 배경
- [cartridges](https://arxiv.org/abs/2506.06266)는 긴 문서 대신 문서마다 학습한 작은 kv cache인 cartridge를 씀
- 이때 cartridge는 student 자신을 teacher로 학습함
- 이 프로젝트는 teacher를 더 큰 모델로 바꾸면 cartridge가 더 나아지는지 확인

## 요약
- [teacher별 정확도](#teacher별-정확도): 더 큰 teacher로 학습하면 나아지는지 → 나아지지 않고 태그 없음만 늘어남
  - [logprob 채점](#logprob-채점): 태그 없음과 상관없이 채점하면 → 여전히 self와 비슷함

## 한계
- student는 llama-3.2-3b-instruct 하나, 벤치마크는 longhealth만 사용
- synthesis는 cartridges 레포의 3×65536개보다 적음
- cot prompt가 `<answer>`가 아닌 여러 태그로 쓴 response를 학습시켜, 태그 없음이 늘었을 수 있음

## 남은 실험
- teacher response가 잘린 synthesis를 빼고 다시 학습해, cross의 태그 없음이 줄어드는지 확인
- student를 7b급 모델로 키워도 더 큰 teacher가 나아지지 않는지 확인

## 공통 설정
- 각 실험의 설정에 따로 적지 않으면 아래 값을 사용
#### 용어
- student: cartridge를 붙여 평가하는 llama-3.2-3b-instruct
- teacher: synthesis를 쓰고 response token마다 분포를 주는 모델
- self, cross: teacher가 student 자신인, llama-3.1-8b-instruct인 cartridge
- base: 문서 없이 question만 받은 student
- icl: 환자 10명의 기록 전체를 prompt에 넣은 student
- synthesis: teacher가 환자 기록 일부를 보고 쓴 question과 response
- cot 비율: synthesis question에 cot prompt를 붙이는 비율
- 태그 없음: response에 닫힌 `<answer>` 태그가 없는 문제
#### synthesis와 cartridge
- synthesis는 cartridges 레포의 llama 설정과 같음
- response token마다 teacher top-20 logprob 저장
- cartridge는 2048 token, student가 response token마다 teacher top-20 분포를 따르도록 학습
- adamw, learning rate 2e-2, batch 64, 2 epoch
#### 평가
- longhealth 환자 10명의 객관식 200문제, cartridges 레포의 cot prompt
- temperature 0.3, 최대 생성 길이 1024 token
- `<answer>` 태그 안 text와 가장 비슷한 선택지로 채점, 태그 없음은 오답
- seed 0, 1, 2 평균, 그림의 ±는 seed 사이 표준편차

## 실험

### teacher별 정확도
- teacher를 student보다 큰 모델로 바꾸면 cartridge 정확도가 오르는지 확인
- self와 cross cartridge를 synthesis 수와 cot 비율별로 학습하고 base, icl과 비교
#### 설정
- 잘림: 최대 생성 길이에 닿고 틀린 문제
- 반복: response 끝에서 200~150번째 글자 50개가 그 앞에 5번 이상 나오는 문제
#### 결과
![](figures/Llama-3.2-3B-Instruct/longhealth_teacher_accuracy.png)
- 16384개에서는 cross가 self보다 낮고, 65536개에서는 비슷함
- cross는 cot 비율보다 synthesis 수에 따라 크게 오름
- cross는 태그 없음이 self보다 많고, 대부분 잘림이나 반복
- 따라서 더 큰 teacher로 바꿔도 cartridge는 나아지지 않고 태그 없음만 늘어남

### logprob 채점
- [teacher별 정확도](#teacher별-정확도)에서 cross는 태그 없음이 많아, 태그 없음과 상관없이 채점해도 self와 비슷한지 확인
- 선택지마다 `<answer>` 뒤 선택지 token의 평균 logprob이 가장 높은 것을 예측으로 봄
#### 설정
- 샘플링하지 않아 seed 없이 한 번
#### 결과
![](figures/Llama-3.2-3B-Instruct/longhealth_logprob_scoring.png)
- 65536개에서 self와 cross가 비슷함
- 16384개 cartridge는 base와 비슷함
- cartridge는 모두 icl에 못 미침
- 따라서 태그 없음과 상관없이 cross는 self보다 낫지 않음
