# E0-PR-008 â€” Excel Qualification Harness Contract v1

**Status:** IMPLEMENTATION CONTRACT â€” EPIC 0 SKELETON  
**Baseline:** E0-PR-007 accepted/merged  
**Scope:** Windows qualification command/report schema + Excel COM runner boundary

## 1. Purpose

This contract defines a fail-closed qualification harness for Microsoft Excel
Desktop compatibility.  It does **not** implement workbook generation/fill,
approval workflow, or the canonical valuation engine.

The legacy workbook remains an output/compatibility artifact.  CenValue RE
calculation remains canonical.

## 2. Qualification states

The only report states are:

- `PASS`
- `FAILED`
- `NOT_QUALIFIED`

`NOT_QUALIFIED` is not PASS and must remain visible to callers.

A report may be `PASS` only when all of the following are evidenced:

1. an actual Microsoft Excel Desktop COM execution occurred;
2. the evidence is bound to the exact workbook SHA-256;
3. the workbook was opened with arbitrary external-link updates disabled;
4. Excel `CalculateFullRebuild` completed;
5. an Excel version is recorded;
6. every required checkpoint in the versioned manifest is present and passes
   the frozen per-checkpoint comparison policy.

Missing Excel, missing COM capability, runner failur, incomplete recalc
evidence or link-update-policy evidence produces `NOT_QUALIFIED`, never PASS.

Actual Excel evidence with failed/missing/unexpected required checkpoints
produces `FAILED`.

## 3. Report schema v1

Every report records:

- `schema_version`;
- `status`;
- `reason_cod` + bounded reason;
- `profile_id`;
- `profile_version`;
- exact `workbook_sha256`;
- `manifest_id`;
- `manifest_version`;
- `checkpoint_set_sha256`;
- runner id/version;
- Excel version when available;
- `actual_excel_evidence`;
- `full_recalculation_performed`;
- `opened_without_link_updates`;
- ordered per-checkpoint results including expected/actual/pass/reason.

The schema constructor itself rejects a `PASS` report that lacks actual Excel
evidence, full recalculation evidence, no-link-update evidence, Excel version,
or an all-pass checkpoint set.

## 4. Runner port

`src/re/ports/excel_qualification.py` owns the framework-independent runner
contract.

The application service must not import `win32com`, COM types, Excel APIs or
adapter implementation.

## 5. Windows COM adapter

`WindowsExcelCOMRunner` is adapter infrastructure.

Target behavior:

1. lazily load pywin32;
2. create isolated `Excel.Application` through `DispatchEx`;
3. keep Excel hidden and disable alerts;
4. open workbook with `UpdateLinks=0` and read-only mode;
5. execute `CalculateFullRebuild`;
6. wait for Excel calculation state `xlDone`;
7. read only the requested `Sheet!A1] checkpoint values;
8. close workbook without saving;
9. quit Excel;
10. return evidence bound to the workbook SHA-256.

The runner must report unavailable rather than claiming PASS when:

-´±…Ñ™½É´¥Ì¹½Ğ]¥¹‘½İÌì(´Áåİ¥¸ÌÈ=4ÍÕÁÁ½ÉĞ¥ÌÕ¹…Ù…¥±…‰±”ì(´5¥É½Í½™Ğá•°•Í­Ñ½À…¹¹½Ğ‰”…Ñ¥Ù…Ñ•¸((ŒŒ€Ø¸EÕ…±¥™¥…Ñ¥½¸½µµ…¹()½µµ…¹µ½‘Õ±”è()ÁåÑ¡½¸€µ´ÍÉŒ¹É”¹…‘…ÁÑ•ÉÌ¹•á•°¹ÅÕ…±¥™¥…Ñ¥½¹}±¥€()I•ÅÕ¥É•¥¹ÁÕÑÌè((´€´µİ½É­‰½½­€(´€´µÁÉ½™¥±”µ¥‘€(´€´µÁÉ½™¥±”µÙ•ÉÍ¥½¹€(´€´µµ…¹¥™•ÍÑ€(´€´µÉ•Á½ÉÑ€()á¥Ğ½‘•Ìè((´€Á€€ôAML(´€Å€€ô%1(´€É€€ô9=Q}EU1%%€()Q¡”½µµ…¹µÕÍĞİÉ¥Ñ”Ñ¡”)M=8É•Á½ÉĞ™½È…±°¹½Éµ…°ÅÕ…±¥™¥…Ñ¥½¸½ÕÑ½µ•Ì¸((ŒŒ€Ü¸áÑ•É¹…°±¥¹­Ì()Q¡”ÅÕ…±¥™¥…Ñ¥½¸ÉÕ¹¹•È½Á•¹Ìİ¥Ñ UÁ‘…Ñ•1¥¹­ÌôÁ€¸()Q¡¥ÌÍ­•±•Ñ½¸‘½•Ì¹½ĞÉ•Í½±Ù”½ÈÍ…¹¥Ñ¥é”±¥¹­Ì¥ÑÍ•±˜¸€Q•µÁ±…Ñ”µÁÉ½™¥±”)Ù…±¥‘…Ñ¥½¸½­¹½İ¸µ±¥¹¬¡…¹‘±¥¹œÉ•µ…¥¹ÌÑ¡”ÕÁÍÑÉ•…´É•ÍÁ½¹Í¥‰¥±¥Ñä‘•™¥¹•‰ä)Ñ¡”á•°½µÁ…Ñ¥‰¥±¥Ñä‘•Í¥¸¸€Q¡”ÉÕ¹¹•ÈµÕÍĞ¹•Ù•ÈÍ¥±•¹Ñ±äÕÁ‘…Ñ”)…É‰¥ÑÉ…Éä¡¥ÍÑ½É¥…°±¥¹­Ì¸((ŒŒ€à¸¡•­Á½¥¹ĞÁ½±¥ä()¡•­Á½¥¹Ğ½µÁ…É¥Í½¸¥Ì‘•±•…Ñ•Ñ¼Ñ¡”Ù•ÉÍ¥½¹•½±‘•¸¥áÑÕÉ”µ…¹¥™•ÍĞ)…¹ÀµAH´ÀÀÔ½µÁ…É…Ñ½È¸€ÀµAH´ÀÀàµÕÍĞ¹½Ğ¥¹ÑÉ½‘Õ”„Í•½¹±½‰…°•ÁÍ¥±½¸)½È‘ÕÁ±¥…Ñ”Ù…±Õ…Ñ¥½¸ÉÕ±•Ì¸((ŒŒ€ä¸$€¼¹¼µá•°ÁÉ½½˜()]¥¹‘½İÌ•¹Ù¥É½¹µ•¹Ğİ¥Ñ Áåİ¥¸ÌÈ¥¹ÍÑ…±±•‰ÕĞ5¥É½Í½™Ğá•°•Í­Ñ½À)Õ¹…Ù…¥±…‰±”µÕÍĞÁÉ½‘Õ”9=Q}EU1%%€¸()$•Ù¥‘•¹”µÕÍĞ•áÁ±¥¥Ñ±äÁÉ½Ù”è((´ÍÑ…ÑÕÌ¥Ì¹½ĞAMLì(´…ÑÕ…±}•á•±}•Ù¥‘•¹”õ™…±Í•€ì(´É•Á½ÉĞÍÑ¥±°½¹Ñ…¥¹ÌÁÉ½™¥±”¥½Ù•ÉÍ¥½¸°İ½É­‰½½¬M!´ÈÔØ°µ…¹¥™•ÍĞ(€¥½Ù•ÉÍ¥½¸½¡•­Á½¥¹ĞµÍ•Ğ¡…Í …¹½É‘•É•¡•­Á½¥¹Ğ%Ì¸()Q¡¥ÌÁÉ½Ù•ÌÍ­¥À½Õ¹…Ù…¥±…‰±”‰•¡…Ù¥½È¥Ì™…¥°µ±½Í•ì¥Ğ¥Ì¹½Ğá•°)ÅÕ…±¥™¥…Ñ¥½¸AML¸((ŒŒ€ÄÀ¸•™•ÉÉ•()9½Ğ¥µÁ±•µ•¹Ñ•‰äÑ¡¥ÌAHè((´İ½É­‰½½¬•¹•É…Ñ¥½¸½™¥±°ì(´Ñ•µÁ±…Ñ”¥¹ÁÕĞµ…ÁÁ¥¹œ•á•ÕÑ¥½¸ì(´•áÑ•É¹…°µ±¥¹¬É•İÉ¥Ñ”¥µÁ±•µ•¹Ñ…Ñ¥½¸ì(´İ½É­‰½½¬Í…Ù”½¡…Í …ÁÁÉ½Ù…°…ÉÑ¥™…ĞÁ¥Á•±¥¹”ì(´á•°¥¹ÍÑ…±±•È½±¥•¹Í¥¹œì(´Q…ÕÉ­¤¥¹Ù½…Ñ¥½¸İ¥É¥¹œì(´…ÁÁÉ½Ù…°É½Õ¹µÑÉ¥Àì(´Ù…±Õ…Ñ¥½¸™½ÉµÕ±…Ìì(´´ÀÄ½´ÀÈ•¹µÑ¼µ•¹…ÁÁÉ…¥Í…°½ÉÉ•Ñ¹•ÍÌ¸()Q¡½Í”É•ÅÕ¥É”±…Ñ•ÈÙ•ÉÑ¥…°Í±¥•Ì…¹½½ÈÉ•…°á•°ÅÕ…±¥™¥…Ñ¥½¸¥¹ÁÕÑÌ¸