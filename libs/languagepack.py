class LanguagePackEN:
	Menu = {}
	Menu['File'] = "File"
	Menu['LoadDictionary'] = "Load Dictionary"
	Menu['LoadException'] = "Load Exception"
	Menu['LoadTM'] = "Load TM"
	Menu['CreateTM'] = "Create TM"
	Menu['Exit'] = "Exit"
	Menu['Help'] = "Help"
	
	Menu['GuideLine'] = "Open Guideline"
	Menu['About'] = "About"

	Menu['Language'] = "Language"
	Menu['Hangul'] = "한글"
	Menu['English'] = "English"

	Menu['LoadLicensePath'] = "Load License file"

	Menu['SaveSetting'] = "Save Setting"

	Button = {}
	Button['Stop'] = "Stop"
	Button['Translate'] = "Translate"
	Button['RenewDatabase'] = "Renew DB"
	Button['OpenOutput'] = "Open Output"
	Button['Browse'] = "Browse"
	Button['SaveConfig'] = "Save Config"
	Button['Save'] = "Save"
	Button['Execute'] = "Execute"
	Button['SelectColor'] = "Select Color"

	Button['SelectBGColor'] = "Select BG Color"
	Button['SelectFontColor'] = "Select Text Color"

	Button['GetTitle'] = "Get Title"	
	Button['Reset'] = "Reset"	
	Button['Load'] = "Load"	
	Button['Save'] = "save"	
	Button['GetReport'] = "Get Report"

	Button['Translate'] = "Translate"
	Button['Swap'] = "Swap"
	Button['Translate'] = "Translate"
	Button['Bilingual'] = "Bilingual Copy"
	Button['TranslateAndBilingual'] = "Translate & Bilingual"
	Button['Copy'] = "Copy"

	Button['Search'] = "Search"
	Button['Delete'] = "Delete"
	Button['Save'] = "Save"
	Button['Update'] = "Update"
	Button['RelativeSearch'] = "Relative Search"
	Button['ReviewReport'] = "Review Report"	

	###########################################################################
	# DOCUMENT TRANSLATOR ONLY START
	###########################################################################

	Button['Convert'] = "Convert"

	###########################################################################
	# DOCUMENT TRANSLATOR ONLY END
	###########################################################################

	Option = {}
	Option['TranslateFileName'] = "Translate file name"
	Option['UpdateTMFile'] = "Update TM file"
	Option['DataOnly'] = "Data Only"
	Option['TurboTranslate'] = "Turbo Translate"
	Option['TMTranslate'] = "TM Translate"
	Option['Hangul'] = "Hangul"
	Option['English'] = "English"
	Option['Google'] = "Google"
	Option['Kakao'] = "Kakao"

	Option['SkipEmptySheet'] = "Skip Empty Sheet"
	Option['TranslateSheetName'] = "Translate Sheet Name"
	Option['ExportSingleSheet'] = "Export 1 sheet/ file"

	Option['DocxCompare'] = "Docx Compare"
	Option['CorruptFileName'] = "Fix Corrupted File Name"
	Option['SavingMode'] = "Saving Mode"

	Option['SheetRemoval'] = "Remove N/A  sheet"
	Option['CompareAll'] = "Compare All"

	Option['Bold'] = "Bold"
	Option['UnderLine'] = "UnderLine"
	###########################################################################
	# DOCUMENT TRANSLATOR ONLY START
	###########################################################################

	Option['UseCloudTM'] = 'Use Cloud TM'

	###########################################################################
	# DOCUMENT TRANSLATOR ONLY END
	###########################################################################
	Option['Bilingual'] = "Bilingual"

	

	Label = {}
	Label['Language'] = "Target: "
	Label['Translator'] = "Translator: "
	Label['Source'] = "Source: "
	Label['ToolOptions'] = "Tool Options: "
	Label['TranslateOptions'] = "Translate Options: "
	Label['Dictionary'] = "Dictionary"
	Label['Exception'] = "Exception"
	Label['TM'] = "TM:"
	

	Label['NumberOfProcess'] = "Number of Process: " #Number of CPU process use

	Label['ExcelOptions'] = "Excel Options: "
	Label['Sheets'] = "Sheets"
	Label['TMOptions'] = "TM Options: "
	Label['OtherOptions'] = "Other Options: "
	Label['ExportTrackingData'] = "Convert Tracking Data: "
	Label['OptimizeDatafile'] = "Optimize XLSX: "
	Label['FixTM'] = "Fix broken TM: "
	Label['SecretKey'] = "Secret Key: "
	Label['MainDB'] = "Main Database: "
	Label['AlternativeDB'] = "Alternative Database: "
	Label['DBSourcePath'] = "Database source: "
	Label['MergeTM'] = "Merge TM files: "
	Label['OldDataTable'] = "Old Data: "
	Label['NewDataTable'] = "New Data: "

	Label['DataSource'] = "Source Data Table: "

	Label['CompareOptions'] = "Compare options: "

	Label['Main_Data_Sheet'] = "Data sheet's name: "
	Label['ID_Col'] = "ID column: "

	Label['BugTitle'] = "Bug title: "
	Label['ReproduceTime'] = "Reproduce Time: "
	Label['TestInfo'] = "Include Test Info"
	Label['IDChar'] = "ID/Character: "
	Label['Report'] = "Report: "
	Label['Steps'] = "Steps: "
	Label['Expected'] = "Expected: "
	Label['Server'] = "Server: "
	Label['Client'] = "Client: "

	Label['SourceText'] = "Source Text: "
	Label['TargetText'] = "Target Text: "
	Label['TargetLanguage'] = "Target Language: "

	Label['Database'] = "Database: "
	Label['Exception'] = "Exception: "
	Label['TranslationMemory'] = "Translation Memory: "
	Label['Header'] = "Header: "

	Label['SecretKey'] = "Subscription key: "
	Label['DBSource'] = "Database Source: "
	Label['MainDB'] = "Main Database: "
	Label['SubDB'] = "Alternative Database: "

	Label['Search'] = "Search: "

	Label['Search'] = "Search: "
	
	Label['TestCaseList'] = "Test case: "
	Label['TestProject'] = "Test project: "
	Label['TestFeature'] = "Test feature: "

	Label['Serial'] = "Device Serial number: "

	Label['LicensePath'] = "License path: "

	Label['ProjectKey'] = "Project key:"

	Label['SourceLanguage'] = "Source language:"
	Label['MainLanguage'] = "Primary language:"
	Label['SecondaryLanguage'] = "Secondary language:"

	###########################################################################
	# DOCUMENT TRANSLATOR ONLY START
	###########################################################################
	
	Label['TMFileConversion'] = "TM File Conversion"
	Label['TMFileUpload'] = "TM File Upload"
	Label['CloudTMOptions'] = "Cloud TM Options:"
	
	###########################################################################
	# DOCUMENT TRANSLATOR ONLY END
	###########################################################################
	Label['Reproducibility'] = "Reproducibility:"
	Label['EnvInfo'] = "Enviromental Information:"

	Label['PreConition'] = "Pre-condition:"

	Tab = {}
	Tab['Main'] = "Main Menu"
	Tab['General'] = "General Setting"
	Tab['Translator'] = "Translate Setting"
	Tab['Excel'] = "Excel Setting"
	Tab['Docx'] = "Docx Setting"
	
	Tab['Debug'] = "Process details"

	Tab['Utility'] = "Utility"
	
	Tab['Comparison'] = "XLSX Comparison"
	Tab['StructuredCompare'] = "Deep Comparison"

	Tab['Optimizer'] = "Optimizer"

	Tab['FileComparison'] = "File Comparison"
	Tab['FolderComparison'] = "Draft Comparison"

	Tab['BugWriter'] = "Bug Writer"
	Tab['SimpleTranslator'] = "Simple Translator"
	Tab['TMEditor'] = "TM Editor"

	Tab['DataLookup'] = "Data Lookup"
	Tab['EnglishValidator'] = "English Validator"

	Tab['MultiDeepCompare'] = "Multi Deep Comparison"

	Tab['AutoExec'] = "Automation Execution"

	Tab['TMManager'] = "TM Manager"
	Tab['DBUploader'] = "DB Uploader"

	Tab['DBSeacher'] = "Search"

	Tab['CustomBugWriter'] = "Custom Writer"

	###########################################################################
	# DOCUMENT TRANSLATOR ONLY START
	###########################################################################

	Tab['TMConverter'] = "TM Converter"

	###########################################################################
	# DOCUMENT TRANSLATOR ONLY END
	###########################################################################

	ToolTips = {}

	ToolTips['UpdateTMFile'] = "Update the new translate result to TM file."
	ToolTips['TMTranslate'] = "Use the previous translation result to speed up the process."
	ToolTips['TMPrepare'] = "To correct the TM that has been save before."
	ToolTips['DataOnly'] = "Displayed text will be translate instead of the formula."
	ToolTips['TurboTranslate'] = "When translating to English, number and Non-Hangul text will be ignored."
	ToolTips['AppInit'] = "Initializing application."
	ToolTips['AppInitDone'] = "Initialisation complete."
	ToolTips['SetLanguage'] = "Target language is set to "
	ToolTips['SetTranslator'] = "Translator Agent is set to "
	ToolTips['SelectExcpt'] = "Please select Exception List."
	ToolTips['ExcptUpdated'] = "Exception List is Updated."
	ToolTips['SelectTM'] = "Please select Translation Memory file."
	ToolTips['TMUpdated'] = "Translation Memory file is Updated."	
	ToolTips['SelectDB'] =  "Please select Dictionary list."
	ToolTips['DBUpdated'] = "Dictionary list is Updated."
	ToolTips['SelectSource'] = "Please select source document."
	ToolTips['SourceSelected'] = "Document list is updated."
	ToolTips['SourceNotSelected'] = "Document is not selected…"
	ToolTips['SourceDocumentEmpty'] = "No document is selected"
	ToolTips['DocumentLoad'] = "Loading document…"
	ToolTips['TranslateFail'] = "Fail to translate the document due to API error"
	ToolTips['NoDictUse'] = "Translate without DB"
	ToolTips['DictUse'] = "Translate with DB"
	ToolTips['TMUpdating'] = "Updating the Translation Memory file…"
	ToolTips['TMCorrecting'] = "Correcting the Translation Memory file…"
	ToolTips['TranslateTimeSpend'] = "Total translate time: "
	ToolTips['AppLanuageUpdate'] = "Update app language to "
	ToolTips['TranslateFileName'] = "Name of the output file will be translated to target language."
	ToolTips['TranslateSheetName'] = "Sheet name from workbook file will be translated."
	ToolTips['FixCorruptedName'] = "Fix the corrupted name of source file to readable format."

	ToolTips['SheetRemoval'] = "If sheet is not selected, it will be removed."

	ToolTips['FilePath'] = "File Path: "

	ToolTips['CompareAll'] = "If unchecked, only \"Data\" sheet is checked"
	ToolTips['Bold'] = "Bold the text on changed cell."
	ToolTips['UnderLine'] = "Underline the text in the changed cell."

	ToolTips['ConfigSaved'] = "App language is updated."
	ToolTips['DocumentLoaded'] = "Document is loaded."
	ToolTips['TMCreated'] = "New Translation Memory file is created."
	ToolTips['Translating'] = "Translating..."
	ToolTips['TMResultFound'] = "Translation Memory result found..."
	ToolTips['TMResultNotFound'] = "Translation Memory result not found..."
	ToolTips['Translated'] = "Translated..."
	ToolTips['TranslateFail'] = "Fail to translate..."
	ToolTips['Copied'] = "Copied to Clipboard..."
	ToolTips['LanguageSet'] = "Target language is set to "
	ToolTips['GenerateBugTitle'] = "Generating bug title."
	ToolTips['GeneratedBugTitle'] = "Bug title is generated."
	ToolTips['GenerateBugTitleFail'] = "Fail to generate bug title."
	ToolTips['GenerateBugReport'] = "Generating report details."
	ToolTips['ClipboardRemoved'] = "Content in clipboard is removed."
	ToolTips['GeneratedBugReport'] = "Bug report is generated."
	ToolTips['GenerateBugReportFail'] = "Fail to generate bug report."	
	ToolTips['LoadReport'] = "Do you want to load the report from last session?"
	###########################################################################
	# DOCUMENT TRANSLATOR ONLY START
	###########################################################################

	ToolTips['UseCloudTM'] = 'Use the Cloud TM instead of local TM.'
	
	###########################################################################
	# DOCUMENT TRANSLATOR ONLY END
	###########################################################################

	ToolTips['Bilingual'] = "Original text is kept in the comment."

	Notice = {}



class LanguagePackKR:
	Menu = {}
	Menu['File'] = "파일"
	Menu['LoadDictionary'] = "사전 목록 로드"
	Menu['LoadException'] = "예외 목록 로드"
	Menu['LoadTM'] = "하중 번역 메모리 목록"
	Menu['CreateTM'] = "변환 메모리 목록 만들기"
	Menu['Exit'] = "퇴장"
	Menu['Help'] = "도움"
	Menu['GuideLine'] = "공개 가이드라인"
	Menu['About'] = "정보"

	Menu['Language'] = "언어"
	Menu['Hangul'] = "한글"
	Menu['English'] = "English"
	
	Menu['LoadLicensePath'] = "라이센스 파일로드"

	Menu['SaveSetting'] = "설정 저장"

	Button = {}
	Button['Stop'] = "중지하다"
	Button['Translate'] = "번역하다"
	Button['RenewDatabase'] = "새로 고치다"
	Button['OpenOutput'] = "출력 폴더 열기"
	Button['Browse'] = "찾아보기"
	Button['SaveConfig'] = "구성 저장"
	Button['Save'] = "저장"
	Button['Execute'] = "실행"
	Button['SelectColor'] = "색상 선택"

	Button['SelectBGColor'] = "배경 색 선택"
	Button['SelectFontColor'] = "텍스트 색상 선택"

	Button['Translate'] = "옮기다"
	Button['Swap'] = "교환"
	Button['Bilingual'] = "이중 언어"
	Button['TranslateAndBilingual'] = "번역 및 이중 언어"
	Button['Copy'] = "부"

	Button['Search'] = "검색"
	Button['Delete'] = "지우다"
	Button['Save'] = "저장"
	Button['Update'] = "최신 정보"
	Button['RelativeSearch'] = "상대 검색"
	Button['ReviewReport'] = "보고서 검토"	

	Option = {}
	Option['TranslateFileName'] = "파일 이름 변환"
	Option['UpdateTMFile'] = "메모리 파일 업데이트"
	Option['DataOnly'] = "셀 값 변환"
	Option['TurboTranslate'] = "터보 변환 모드"
	Option['TMTranslate'] = "메모리로 변환"
	Option['Hangul'] = "한글"
	Option['English'] = "영문"
	Option['Google'] = "Google"
	Option['Kakao'] = "Kakao"

	Option['SkipEmptySheet'] = "빈 시트 건너뛰기"
	Option['TranslateSheetName'] = "시트 이름 변환"
	Option['ExportSingleSheet'] = "1장/파일"

	Option['DocxCompare'] = "문서 비교"
	Option['CorruptFileName'] = "손상된 파일 이름 수정"
	Option['SavingMode'] = "저장 모드"

	Option['SheetRemoval'] = "N/A 시트 제거"
	Option['CompareAll'] = "모든 데이터 비교"

	Option['Bold'] = "굵게"
	Option['UnderLine'] = "밑줄"

	Option['Bilingual'] = "이중 언어"

	Button['GetTitle'] = "타이틀 받기"	
	Button['Reset'] = "초기화"	
	Button['Load'] = "하중"	
	Button['Save'] = "저장"	
	Button['GetReport'] = "보고서 받기"	

	Button['Load'] = "하중"	


	Label = {}
	Label['Language'] = "대상 언어"
	Label['Translator'] = "번역기"
	Label['Source'] = "원본 문서: "
	Label['ToolOptions'] = "도구 옵션"
	Label['TranslateOptions'] = "변환 옵션"
	Label['Dictionary'] = "사전"
	Label['Exception'] = "예외"
	Label['TM'] = "변환 메모리:"

	Label['NumberOfProcess'] = "프로세스 사용 횟수" #Number of CPU process use

	Label['ExcelOptions'] = "Excel 옵션"
	Label['Sheets'] = "시트"
	Label['TMOptions'] = "번역 메모리 옵션: "
	Label['OtherOptions'] = "기타 옵션: "
	Label['ExportTrackingData'] = "추적 데이터 변환: "
	Label['OptimizeDatafile'] = "XLSX 최적화: "
	Label['FixTM'] = "깨진 TM 수정: "
	Label['SecretKey'] = "비밀 키: "
	Label['MainDB'] = "메인 데이터베이스: "
	Label['AlternativeDB'] = "대체 데이터베이스: "
	Label['DBSourcePath'] = "데이터베이스 원본: "
	Label['MergeTM'] = "번역 메모리 파일 병합: "

	Label['OldDataTable'] = "이전 데이터 원본: "
	Label['NewDataTable'] = "새 데이터 원본: "

	Label['DataSource'] = "원본 데이터 테이블: "

	Label['CompareOptions'] = "옵션 비교: "

	Label['Main_Data_Sheet'] = "데이터 시트 이름: "
	Label['ID_Col'] = "ID 열 : "

	Label['BugTitle'] = "버그 제목: "
	Label['ReproduceTime'] = "재생산 시간: "
	Label['TestInfo'] = "테스트 정보 포함"
	Label['IDChar'] = "아이디 / 캐릭터: "
	Label['Report'] = "보고서: "
	Label['Steps'] = "단계: "
	Label['Expected'] = "예상 결과: "

	Label['Server'] = "섬기는 사람: "
	Label['Client'] = "고객: "

	Label['SourceText'] = "소스 텍스트: "
	Label['TargetText'] = "대상 텍스트: "
	Label['TargetLanguage'] = "대상 언어: "

	Label['Database'] = "데이터 베이스: "
	Label['Exception'] = "예외: "
	Label['TranslationMemory'] = "번역 메모리: "
	Label['Header'] = "헤더: "

	Label['SecretKey'] = "구독 키: "
	Label['DBSource'] = "데이터베이스 소스: "
	Label['MainDB'] = "주요 데이터베이스: "
	Label['SubDB'] = "대체 데이터베이스: "

	Label['Search'] = "검색:"

	Label['TestCaseList'] = "테스트 케이스: "	

	Label['TestProject'] = "프로젝트 테스트: "
	Label['TestFeature'] = "테스트 기능: "

	Label['Serial'] = "장치 일련 번호: "

	Label['LicensePath'] = "라이센스 경로 :"

	Label['ProjectKey'] = "프로젝트 키 :"

	Label['SourceLanguage'] = "소스 언어:"
	Label['MainLanguage'] = "기본 언어:"
	Label['SecondaryLanguage'] = "제2언어:"

	Label['Reproducibility'] = "재현빈도:"
	Label['EnvInfo'] = "환경정보:"

	Label['PreConition'] = "전제 조건"

	Tab = {}
	Tab['Main'] = "메인 메뉴"
	Tab['General'] = "일반 설정"
	Tab['Translator'] = "번역기 설정"
	Tab['Excel'] = "엑셀 설정"
	Tab['Docx'] = "문서 설정"
	Tab['Debug'] = "디버거"

	Tab['Utility'] = "유틸리티"

	Tab['Comparison'] = "XLSX 비교"
	Tab['StructuredCompare'] = "깊은 비교"

	Tab['Optimizer'] = "최적화"

	Tab['FileComparison'] = "파일 비교"
	Tab['FolderComparison'] = "초안 비교"

	Tab['BugWriter'] = "버그 라이터"
	Tab['SimpleTranslator'] = "간단한 번역기"
	Tab['TMEditor'] = "번역 메모리 편집기"

	Tab['DataLookup'] = "데이터 조회"
	Tab['EnglishValidator'] = "영어 검사기"

	Tab['MultiDeepCompare'] = "멀티 딥 비교"

	Tab['AutoExec'] = "자동화 실행"

	Tab['TMManager'] = "TM 관리자"
	Tab['DBUploader'] = "DB 업 로더"

	Tab['DBSeacher'] = "검색"
	
	Tab['CustomBugWriter'] = "커스텀 라이터"

	ToolTips = {}

	ToolTips['UpdateTMFile'] = "번역 메모리 파일 업데이트"
	ToolTips['TMTranslate'] = "번역 메모리 사용"
	ToolTips['TMPrepare'] = "번역 메모리 관리"
	ToolTips['DataOnly'] = "결과값 표시"
	ToolTips['TurboTranslate'] = "터보 번역"
	ToolTips['AppInit'] = "응용 프로그램 초기화."
	ToolTips['AppInitDone'] = "초기화가 완료되었습니다."
	ToolTips['SetLanguage'] = "언어 선택 "
	ToolTips['SetTranslator'] = "번역툴 선택 "
	ToolTips['SelectExcpt'] = "예외사항을 선택해 주세요"
	ToolTips['ExcptUpdated'] = "예외사항 업데이트 완료"
	ToolTips['SelectTM'] = "번역 메모리 선택해 주세요"
	ToolTips['TMUpdated'] = "번역 메모리 업데이트 완료"	
	ToolTips['SelectDB'] =  "DB 선택"
	ToolTips['DBUpdated'] = "DB 업데이트 완료"
	ToolTips['SelectSource'] = "문서 선택"
	ToolTips['SourceSelected'] = "문서 선택 완료"
	ToolTips['SourceNotSelected'] = "문서 선택되지 않음"
	ToolTips['SourceDocumentEmpty'] = "문서 없음"
	ToolTips['DocumentLoad'] = "문서 없음"
	ToolTips['TranslateFail'] = "문서 로딩중"
	ToolTips['NoDictUse'] = "DB 미적용"
	ToolTips['DictUse'] = "DB 적용"
	ToolTips['TMUpdating'] = "번역 메모리 파일 업데이트 중"
	ToolTips['TMCorrecting'] = "번역 메모리 파일 수정 중"
	ToolTips['TranslateTimeSpend'] = "총 번역 시간 "
	ToolTips['AppLanuageUpdate'] = "앱 언어 한글/영문 업데이트 "

	ToolTips['TranslateFileName'] = "출력 파일의 이름은 대상 언어로 번역됩니다."
	ToolTips['TranslateSheetName'] = "통합 문서 파일의 시트 이름이 번역됩니다."
	ToolTips['FixCorruptedName'] = "손상된 소스 파일 이름을 읽을 수 있는 형식으로 수정합니다."

	ToolTips['SheetRemoval'] = "시트를 선택하지 않으면 시트가 제거됩니다."

	ToolTips['FilePath'] = "파일 경로: "

	ToolTips['CompareAll'] = "확인되지 않으면 \"Data\" 시트만 선택됩니다."
	ToolTips['Bold'] = "변경된 셀의 텍스트를 굵게 합니다."
	ToolTips['UnderLine'] = "변경된 셀의 텍스트를 밑줄로 정렬합니다."

	ToolTips['ConfigSaved'] = "앱 언어가 업데이트되었습니다."
	ToolTips['DocumentLoaded'] = "문서가 적재되었습니다."
	ToolTips['TMCreated'] = "새로운 번역 메모리 파일이 생성됩니다."
	ToolTips['Translating'] = "번역 중 ..."
	ToolTips['TMResultFound'] = "번역 메모리 결과를 찾았습니다."
	ToolTips['TMResultNotFound'] = "번역 메모리 결과를 찾을 수 없습니다."
	ToolTips['Translated'] = "번역..."
	ToolTips['TranslateFail'] = "번역 실패."
	ToolTips['Copied'] = "클립 보드에 복사."
	ToolTips['LanguageSet'] = "대상 언어가"
	ToolTips['GenerateBugTitle'] = "버그 제목 생성"
	ToolTips['GeneratedBugTitle'] = "버그 제목이 생성됩니다."
	ToolTips['GenerateBugTitleFail'] = "버그 제목을 생성하지 못했습니다."
	ToolTips['GenerateBugReport'] = "보고서 세부 사항 생성"
	ToolTips['ClipboardRemoved'] = "클립 보드의 내용이 제거되었습니다."
	ToolTips['GeneratedBugReport'] = "버그 리포트가 생성됩니다."
	ToolTips['GenerateBugReportFail'] = "버그 보고서를 생성하지 못했습니다."
	ToolTips['LoadReport'] = "마지막 세션의 보고서를 로드하시겠습니까?"
	
	ToolTips['Bilingual'] = "원본 텍스트는 주석에 보관됩니다."

	Notice = {}
