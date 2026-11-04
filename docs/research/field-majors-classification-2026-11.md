# Example majors where the Ministry's guide has too little (decision 073)

**Why:** each card on the «جرّب قبل أن تقرر» result shows example majors. The Ministry's 2026–2027 guide to the university lists has no health or education field, and one major in its arts and humanities field («تصميم المنتجات»). Decision 069 kept those fields honest with a note, and CLAUDE.md forbids unsourced lists, so the owner chose an official list to fill the gap (2026-11-04).

**Source:** «التصنيف السعودي الموحد للمستويات والتخصصات التعليمية» 1441هـ – 2020م, Ministry of Education (its cover carries the Ministry's name and www.moe.gov.sa). No copy was found on moe.gov.sa; the copies read are hosted by King Saud University:
- index of majors by field, pages 710–717 (the source the site links): https://vrea.ksu.edu.sa/sites/vrea.ksu.edu.sa/files/users/user204/%D9%83%D8%B4%D8%A7%D9%81%20%D8%A7%D9%84%D8%AA%D8%AE%D8%B5%D8%B5%D8%A7%D8%AA%20%D8%AD%D8%B3%D8%A8%20%D8%A7%D9%84%D9%85%D8%AC%D8%A7%D9%84%D8%A7%D8%AA%20%D8%A7%D9%84%D8%AA%D8%B9%D9%84%D9%8A%D9%85%D9%8A%D8%A9.pdf
- the whole document (cover read for its issuer): https://vrea.ksu.edu.sa/sites/vrea.ksu.edu.sa/files/imce_images/dlyl_tsnyf_lmstwyt_wltkhsst_ltlymy.pdf

**How it was read (2026-11-04):** the PDF's Arabic text doesn't extract (its fonts have no Unicode map), so `scripts/check_quote.py` can't verify these names. The pages were rendered to images and read directly, each name below against its code. Search snippets were not used.

| Field on the card | Name used | Code | Page |
|---|---|---|---|
| الصحة والرعاية | الطب | 0912 | 716 |
| | دراسات طب الأسنان | 0911 | 716 |
| | الصيدلة | 0916 | 717 |
| | التمريض والقبالة | 0913 | 716 |
| التعليم | الطفولة المبكرة | 011201 | 710 |
| | التربية الخاصة | 011308 | 710 |
| | التعليم الابتدائي | 011313 | 711 |
| | تقنيات التعليم | 011105 | 710 |
| الفنون والعلوم الإنسانية | التصميم الجرافيكي والوسائط الرقمية | 021102 | 711 |
| | تصميم المنتجات | 021202 | 711 |
| | التاريخ | 022202 | 711 |
| | اللغة الإنجليزية والترجمة | 023103 | 711 |

**What this is and isn't:** the classification names fields of study. It doesn't say a major is offered in a scholarship list or at a given university. So the cards call them examples, and for arts and humanities the details add that the guide itself names only «تصميم المنتجات».

**The other seven fields** use names from the Ministry's guide itself (`majors_from: guide`). A test checks each one against `universities.json`. They were chosen by hand to be recognisable, because the guide's first four names aren't a fair picture of a field (engineering began with chemical and materials).
