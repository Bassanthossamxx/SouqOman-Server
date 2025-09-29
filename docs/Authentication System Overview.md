# Authentication System Overview

This document describes how authentication works in the project: core concepts, endpoints, required data, and regional (Oman) specific rules used for validating user identity and location.

---
---
## 1. Authentication Flow (Current State)
1. User registers with required profile data (no OTP yet)
2. System issues a pair of JWT tokens (access + refresh)
3. User authenticates subsequent requests using the access token (Authorization: Bearer ...)
4. (Future) OTP verification will be enforced

---
## 2. Endpoints :
| Endpoint | Method | Description | Auth Required | Returns |
|----------|--------|-------------|---------------|---------|
| /auth/register | POST | Create a new user with profile + phone | No | access + refresh tokens |
| /auth/login | POST | Authenticate via phone + password | No | access + refresh tokens |
| /auth/logout | POST | Invalidate current token (implementation TBD: blacklist) | Yes | status message |
| /auth/me | GET | Return authenticated user profile | Yes | user object |


---
## 3. User Model Fields
| Field | Description | Notes / Constraints |
|-------|-------------|---------------------|
| full_name_ar | Full name in Arabic | Required (UTF-8) |
| full_name_en | Full name in English | Required (Latin chars) |
| email | Email address | Unique (if enforced); optional vs required depends on final policy |
| phone | Oman phone number | Must follow +968 standard below; used for login |
| governorate | Governorate selection | Must be one from controlled list |
| wilayat | Wilayat inside selected governorate | Must correspond to chosen governorate |
| password | Hashed credential | Must meet minimum complexity policy (TBD) |

Optional future fields: is_phone_verified , otp.

---
## 4. JWT & Security Notes
- Access + refresh tokens (standard lifetimes to be defined in settings)
- Store secrets in environment variables (never commit keys)
- logout implementation TBD (blacklist)
- Future roadmap:
  - OTP (Meta / WhatsApp) for phone verification during registration
---
## 5. Oman Phone Number Standard
| Aspect | Rule |
|--------|------|
| Country Code | +968 |
| Local Length | 8 digits |
| Formatting | No leading 0 after country code |
| Example | +96812345678 |

Validation Regex (conceptual): ^\+968[0-9]{8}$

---
## 6. Governorate & Wilayat Reference
Used to standardize location fields during registration and future listing filtering.
Source Reference: https://omannews.gov.om/pages/174/show/561

| Governorate (English) | المحافظة (Arabic) | Wilayats (English) | الولايات (Arabic) |
|-----------------------|-------------------|--------------------|-------------------|
| Muscat | محافظة مسقط | Muscat, Mutrah, Al Amirat, Bawshar, Seeb, Qurayyat | مسقط، مطرح، العامرات، بوشر، السيب، قريات |
| Dhofar | محافظة ظفار | Salalah, Taqah, Mirbat, Rakhyut, Thumrait, Dhalkut, Al Mazyunah, Muqshin, Shalim & Hallaniyat Islands, Sadah | صلالة، طاقة، مرباط، رخيوت، ثمريت، دلكوت، المزيونة، مقشن، شليم وجزر الحلانيات، صعدة |
| Musandam | محافظة مسندم | Khasab, Diba, Bukha, Madha | خصب، دبا، بخا، مدحاء |
| Al Buraimi | محافظة البريمي | Al Buraimi, Mahdah, As Sunaynah | البريمي، محضة، السنينة |
| Ad Dakhiliyah | محافظة الداخلية | Nizwa, Samail, Bahla, Adam, Al Hamra, Manah, Izki, Bidbid, Jebel Akhdar | نزوى، سمائل، بهلاء، ادام، الحمراء، منة، ازكي، بِدبد، جبل الأخضر |
| Al Batinah North | محافظة شمال الباطنة | Sohar, Shinas, Liwa, Saham, Al Khaburah, Al Suwaiq | صحار، شناص، ليوا، صحار، الخابورة، السويق |
| Al Batinah South | محافظة جنوب الباطنة | Rustaq, Al Awabi, Nakhal, Wadi Al Ma‘awil, Barka, Al Musannah | الرستاق، العوابي، نخل، وادي المعاول، بركاء، المهاشنة |
| Ash Sharqiyah North | محافظة شمال الشرقية | Ibra, Al Mudhaibi, Bidiya, Al Qabil, Wadi Bani Khalid, Dema Wa At-Tayeen | إبراء، المضيبي، بدية، القابل، وادي بني خالد، دما والطائيين |
| Ash Sharqiyah South | محافظة جنوب الشرقية | Sur, Al Kamil Wal Wafi, Jalan Bani Bu Hassan, Jalan Bani Bu Ali, Masirah | صور، الكامل والوافي، جعلان بني بو حسن، جعلان بني بو علي، مصيرة |
| Ad Dhahirah | محافظة الظاهرة | Ibri, Yanqul, Dhank | عبري، ينقل، دنك |
| Al Wusta | محافظة الوسطى | Haima, Mahout, Duqm, Al Jazer | هيما، محوت، الدقم، الجزر |

---
