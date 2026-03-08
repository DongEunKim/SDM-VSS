# GitHub 푸시 가이드 – ref. 링크/서브모듈 문제 해결

## 현재 상황

`ref.` 폴더 안에 다른 저장소들(eclipse-kuksa, VSS 등)을 **그대로 클론한 상태**로 들어 있습니다.  
각 하위 폴더마다 `.git`이 있어서 Git이 이를 **서브모듈처럼** 취급하려 하지만,  
최상위 저장소에는 `.gitmodules`가 없어 **링크가 제대로 동작하지 않습니다.**

## 선택지

### 방법 1: 모든 내용을 하나의 저장소에 포함 (추천)

다른 저장소 내용까지 전부 SDM-VSS 한 저장소에 넣어서 푸시하려면,  
`ref.` 안의 각 폴더를 **일반 폴더**로 바꾸면 됩니다.

**사용자 터미널에서 실행:**

```bash
cd /home/ubuntu/workspace/SDM-VSS

# 1. ref./ 내부의 모든 .git 폴더 찾아서 삭제 (중첩된 git 제거)
find ref. -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true

# 2. 변경사항 확인
git status

# 3. ref./ 전체 추가
git add ref.

# 4. 커밋 및 푸시
git add .
git commit -m "ref: 외부 참조 저장소 내용 통합"
git push origin main
```

> ⚠️ `find` 명령 실행 전에 `ref.` 백업을 권장합니다.

---

### 방법 2: 서브모듈로 제대로 설정

`ref.`는 **외부 저장소 링크**만 두고, 실제 내용은 서브모듈로 관리하려면:

**1단계: 기존 ref. 제거 후 서브모듈로 다시 추가**

```bash
cd /home/ubuntu/workspace/SDM-VSS

# 기존 ref. 트래킹 제거 (파일은 유지)
git rm -r --cached ref. 2>/dev/null || true

# ref. 폴더 삭제 (다시 서브모듈로 받을 것이므로)
rm -rf ref.
```

**2단계: .gitmodules 생성 및 서브모듈 추가**

```bash
# 주요 참조 저장소들만 서브모듈로 추가 (필요한 것만 선택)
git submodule add https://github.com/COVESA/vehicle_signal_specification.git ref./VSS/vehicle_signal_specification
git submodule add https://github.com/eclipse-kuksa/kuksa-databroker.git ref./eclipse-kuksa/databroker/kuksa-databroker
git submodule add https://github.com/eclipse-kuksa/kuksa-can-provider.git ref./eclipse-kuksa/providers/kuksa-can-provider
git submodule add https://github.com/eclipse-kuksa/kuksa-csv-provider.git ref./eclipse-kuksa/providers/kuksa-csv-provider
git submodule add https://github.com/eclipse-kuksa/kuksa-dds-provider.git ref./eclipse-kuksa/providers/kuksa-dds-provider
git submodule add https://github.com/eclipse-kuksa/kuksa-python-sdk.git ref./eclipse-kuksa/sdks/kuksa-python-sdk

git add .gitmodules ref.
git commit -m "ref: 서브모듈로 참조 저장소 연결"
git push origin main
```

**3단계: 다른 사람이 클론할 때**

```bash
git clone --recurse-submodules https://github.com/DongEunKim/SDM-VSS.git
# 또는 이미 클론했다면:
git submodule update --init --recursive
```

---

## 요약

| 목적 | 추천 방법 |
|------|-----------|
| 모든 코드를 하나의 저장소에 담아서 푸시 | **방법 1** |
| 외부 저장소를 링크로만 연결해 관리 | **방법 2** |

Cursor 내장 터미널이 멈춘다면, **시스템 터미널**(예: Ubuntu Terminal)에서 위 명령을 실행해 보세요.
