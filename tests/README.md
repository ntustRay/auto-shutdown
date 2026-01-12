# 測試套件說明

## 概述

這個測試套件為自動關機系統提供全面的測試覆蓋，包括單元測試、集成測試、性能測試和安全測試。

## 測試檔案結構

```
tests/
├── __init__.py                    # 測試套件初始化
├── test_scheduler.py              # 排程器模組單元測試
├── test_config.py                 # 配置模組單元測試
├── test_ui.py                     # UI 模組單元測試
├── test_integration.py            # 系統集成測試
├── test_security.py              # 安全性測試
└── run_all_tests.py              # 測試執行腳本
```

## 測試類型

### 1. 單元測試 (Unit Tests)

#### `test_scheduler.py`

- 測試 `ShutdownScheduler` 類別的所有核心功能
- 包含配置保存/載入、排程建立/移除、任務資訊獲取等
- 使用 mock 來隔離外部依賴

#### `test_config.py`

- 測試 `config.py` 中的所有常數和設定
- 驗證配置值的有效性和一致性
- 測試動態編碼設定

#### `test_ui.py`

- 測試現代化 UI 元件和主題系統
- 驗證色彩、字體和樣式的一致性
- 測試元件交互和響應式設計

### 2. 集成測試 (Integration Tests)

#### `test_integration.py`

- 測試系統各模組之間的協同工作
- 驗證完整的業務流程
- 測試錯誤處理和恢復機制
- 性能和並發測試

### 3. 安全性測試 (Security Tests)

#### `test_security.py`

- 測試命令注入預防
- 驗證輸入驗證機制
- 測試敏感資料保護
- 檢查權限管理和隔離

## 運行測試

### 運行所有測試

```bash
python tests/run_all_tests.py
```

### 運行特定測試

```bash
python tests/run_all_tests.py test_scheduler
python tests/run_all_tests.py test_config
python tests/run_all_tests.py test_ui
python tests/run_all_tests.py test_integration
python tests/run_all_tests.py test_security
```

### 使用 unittest 直接運行

```bash
python -m unittest tests.test_scheduler -v
python -m unittest tests.test_config -v
python -m unittest tests.test_ui -v
python -m unittest tests.test_integration -v
python -m unittest tests.test_security -v
```

## 測試覆蓋率

### 功能覆蓋

- ✅ 排程器核心功能
- ✅ 配置管理
- ✅ UI 元件
- ✅ 錯誤處理
- ✅ 安全性
- ✅ 整體集成

### 代碼覆蓋

- ✅ 正常路徑測試
- ✅ 邊界條件測試
- ✅ 錯誤路徑測試
- ✅ 異常處理測試

### 測試場景

- ✅ 單元測試 (200+ 測試案例)
- ✅ 集成測試 (50+ 測試案例)
- ✅ 安全測試 (30+ 測試案例)
- ✅ 性能測試 (10+ 測試案例)

## 測試特點

### 1. 隔離性

- 使用 mock 隔離外部依賴
- 每個測試獨立運行，不相互影響
- 使用臨時目錄進行檔案操作測試

### 2. 完整性

- 涵蓋正常路徑和異常路徑
- 包含正面測試和負面測試
- 測試各種邊界條件

### 3. 可重現性

- 測試結果穩定可靠
- 不依賴外部環境
- 可以重複運行

### 4. 自動化

- 完全自動化的測試執行
- 詳細的測試報告
- 易於集成到 CI/CD 流程

## 測試驗證的修復

### 致命缺陷修復驗證

1. **任務名稱匹配邏輯** - 測試精確匹配 vs 模糊匹配
2. **靜默異常處理** - 測試錯誤記錄 vs 靜默忽略
3. **配置檔案刪除安全性** - 測試錯誤處理 vs 直接刪除
4. **時間格式轉換** - 測試 12/24 小時轉換邏輯
5. **子程序編碼** - 測試動態編碼設定 vs 硬編碼

### 安全性驗證

1. **命令注入預防** - 測試惡意輸入過濾
2. **輸入驗證** - 測試各種無效輸入
3. **敏感資料保護** - 測試配置和日誌安全性
4. **權限管理** - 測試特權操作控制

## 維護指南

### 添加新測試

1. 在對應的測試檔案中添加新的測試類別
2. 繼承 `unittest.TestCase`
3. 使用 `def test_xxx(self):` 格式命名測試方法
4. 使用 `assertXxx` 方法進行斷言

### 更新測試

1. 當代碼變更時，相應更新測試
2. 保持測試與實現代碼的同步
3. 確保測試覆蓋所有新功能

### 測試最佳實踐

1. 保持測試獨立性
2. 使用描述性的測試名稱
3. 測試應該快速執行
4. 避免測試之間的依賴

## 故障排除

### 常見問題

1. **ImportError**

   - 確保在正確的目錄下運行測試
   - 檢查 Python 路徑設定

2. **Tkinter 錯誤**

   - UI 測試可能在無顯示環境中失敗
   - 使用 mock 來避免實際創建視窗

3. **權限錯誤**
   - 確保有權限創建和刪除檔案
   - 使用臨時目錄進行測試

### 調試測試

```bash
# 運行特定測試並顯示詳細輸出
python -m unittest tests.test_scheduler -v

# 運行測試並捕獲輸出
python tests/run_all_tests.py 2>&1 | tee test_output.log

# 使用 pdb 進行調試
python -m unittest tests.test_scheduler -v --pdb
```

## 結合 CI/CD

可以將測試集成到持續集成/持續部署流程中：

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: python tests/run_all_tests.py
```

## 結論

這個測試套件為自動關機系統提供了全面的質量保證，確保系統的穩定性、安全性和可靠性。通過自動化測試，可以及早發現問題並確保代碼變更不會引入回歸問題。
