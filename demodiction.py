# demoDict

colors ={"apple":"red","bannana":"yellow"}
morphology = {"apple":"round","bannana":"rong"}
print(len(colors))
#검색
print(colors["apple"])
#입력
colors["cherry"] = "red"
print(colors)
#삭제
del colors["apple"]
print(colors)
print("삭제")

for item in colors.items():
    print(item)

for itemM in morphology.items():
    print(itemM)


