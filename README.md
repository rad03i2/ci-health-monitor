# CI Health Monitor

A small, dependency-free Python tool for analyzing exported GitHub Actions workflow-run JSON and turning CI history into an actionable health report. It works offline: export run metadata with `gh run list --json ...`, then inspect reliability, failure rate, duration, and recent regressions without sharing repository data with another service.

## Why it exists
CI failures are easy to notice one at a time but harder to evaluate as a trend. CI Health Monitor provides a deterministic local summary that can be archived, compared, or consumed by scripts.

## Features
- Reads a JSON array or `{ "workflow_runs": [...] }` payload.
- Supports GitHub CLI fields (`name`, `workflowName`, `status`, `conclusion`, `createdAt`, `updatedAt`, `url`) and REST-style equivalents.
- Reports totals, success/failure/cancelled/in-progress counts, success rate, average and p95 completed-run duration, consecutive recent failures, and per-workflow statistics.
- Optional workflow filter and configurable unhealthy thresholds.
- Human-readable and JSON output; CI-friendly exit codes.
- Offline, read-only, dependency-free runtime.

## Preview
```text
CI Health: HEALTHY
Runs: 12 | Success: 10 | Failed: 1 | Cancelled: 1
Success rate: 90.9% (completed, non-cancelled)
Average duration: 2m 14s | P95: 4m 08s
Recent consecutive failures: 0
```
The repository intentionally does not include a fabricated screenshot. The terminal preview above reflects the implemented report format.

## Requirements
Python 3.10+.

## Installation
```bash
git clone https://github.com/rad03i2/ci-health-monitor.git
cd ci-health-monitor
python -m pip install -e .
```

## Usage
Export real workflow history with GitHub CLI:
```bash
gh run list --limit 100 --json name,workflowName,status,conclusion,createdAt,updatedAt,url > runs.json
ci-health-monitor runs.json
```
Machine-readable output and policy checks:
```bash
ci-health-monitor runs.json --json
ci-health-monitor runs.json --min-success-rate 95 --max-consecutive-failures 1
ci-health-monitor runs.json --workflow "CI"
```
Exit code `0` means the report meets the configured policy, `1` means unhealthy, and `2` means invalid input or usage.

### Python API
```python
from ci_health_monitor import analyze_runs, load_runs
report = analyze_runs(load_runs("runs.json"), min_success_rate=90)
print(report.success_rate, report.healthy)
```

## Configuration
There is no config file or environment variable requirement. CLI flags are the complete configuration surface. Defaults: minimum success rate `90%`; maximum consecutive failures `2`.

## Project structure
```text
src/ci_health_monitor/   # parser, analysis model, CLI
examples/runs.json       # explicitly synthetic example input
tests/                   # unittest suite
.github/workflows/ci.yml # cross-platform CI
```

## Testing
```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
```
CI runs these checks on Linux, Windows, and macOS with supported Python versions.

## Security & privacy
The tool is read-only and performs no network requests. Run exports can contain repository names and URLs, so review files before sharing them. See [SECURITY.md](SECURITY.md).

## Limitations
This is historical run-metadata analysis, not a live GitHub monitor. It does not fetch logs, identify root causes, retry jobs, or infer flaky tests. Duration accuracy depends on timestamps present in the export. Cancelled/skipped runs are excluded from the success-rate denominator.

## Optional roadmap
Possible future additions include comparison of two snapshots and opt-in live provider adapters. These are not required for the current offline workflow.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Keep changes focused, tested, and dependency-light.

## License
MIT — see [LICENSE](LICENSE).

## Author
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

---

# العربية — مراقب صحة CI

أداة Python صغيرة وبدون اعتماديات تشغيلية لتحليل بيانات تشغيل GitHub Actions المصدّرة وتحويل سجل CI إلى تقرير صحة عملي. تعمل محليًا بالكامل: صدّر بيانات التشغيل بواسطة `gh run list` ثم افحص الاعتمادية ونسبة الفشل والمدة والتراجعات الحديثة دون إرسال بيانات المستودع إلى خدمة أخرى.

## لماذا المشروع؟
من السهل ملاحظة فشل تشغيل منفرد، لكن تقييم الاتجاه عبر عشرات التشغيلات أصعب. توفر الأداة ملخصًا محليًا حتميًا يمكن حفظه أو مقارنته أو استخدامه في السكربتات.

## الميزات
- قراءة مصفوفة JSON أو كائن يحوي `workflow_runs`.
- دعم حقول GitHub CLI والحقول المكافئة في REST.
- إحصاء النجاح والفشل والإلغاء والتشغيل الجاري، ونسبة النجاح، ومتوسط وP95 للمدة، والفشل المتتالي الحديث، وإحصاءات كل Workflow.
- فلترة حسب اسم Workflow وحدود صحة قابلة للتعديل.
- إخراج نصي أو JSON ورموز خروج مناسبة للأتمتة.
- تشغيل محلي، للقراءة فقط، وبدون اعتماديات خارجية.

## المعاينة
يعرض الأمر تقريرًا نصيًا مثل المثال الإنجليزي أعلاه. لا توجد لقطة شاشة مصطنعة؛ يمكن التقاط الطرفية بعد تحليل بياناتك الحقيقية إذا رغبت بعرض مرئي.

## المتطلبات والتثبيت
Python 3.10 أو أحدث:
```bash
git clone https://github.com/rad03i2/ci-health-monitor.git
cd ci-health-monitor
python -m pip install -e .
```

## الاستخدام
```bash
gh run list --limit 100 --json name,workflowName,status,conclusion,createdAt,updatedAt,url > runs.json
ci-health-monitor runs.json
ci-health-monitor runs.json --json
ci-health-monitor runs.json --min-success-rate 95 --max-consecutive-failures 1
```
رمز الخروج `0` يعني أن السياسة محققة، و`1` يعني أن الحالة غير صحية، و`2` يعني خطأ في الإدخال أو الاستخدام.

## Python API
يمكن استيراد `load_runs` و`analyze_runs` كما في المثال الإنجليزي. لا تحتاج الأداة ملف إعداد أو متغيرات بيئة؛ جميع الإعدادات عبر خيارات CLI.

## بنية المشروع والاختبارات
الكود داخل `src/ci_health_monitor`، والاختبارات داخل `tests`، ويوجد مثال اصطناعي معلّم بوضوح في `examples/runs.json` وCI متعدد الأنظمة. للتأكد محليًا:
```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

## الأمان والخصوصية
لا تنفذ الأداة طلبات شبكة ولا تعدّل GitHub. قد يحتوي ملف التصدير أسماء مستودعات وروابط، لذلك راجعه قبل مشاركته. راجع [SECURITY.md](SECURITY.md).

## القيود
الأداة تحلل metadata تاريخية وليست مراقبًا حيًا. لا تقرأ سجلات jobs، ولا تحدد سبب الفشل، ولا تعيد تشغيل jobs، ولا تستنتج الاختبارات المتذبذبة. دقة المدة تعتمد على الطوابع الزمنية المتاحة، والتشغيلات الملغاة/المتخطاة لا تدخل في مقام نسبة النجاح.

## تطوير اختياري
يمكن مستقبلًا إضافة مقارنة snapshotين أو موصلات حية اختيارية، لكن ذلك ليس جزءًا من الوظيفة الحالية.

## المساهمة والترخيص
راجع [CONTRIBUTING.md](CONTRIBUTING.md). المشروع مرخص وفق MIT في [LICENSE](LICENSE).

## المؤلف
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**