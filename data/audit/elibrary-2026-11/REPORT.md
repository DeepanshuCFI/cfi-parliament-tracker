# Lok Sabha full-text audit against eLibrary Sansad (23 Nov 2026)

Source: the Lok Sabha Secretariat's archive at elibrary.sansad.in, collection "Part 1 (Questions And Answers)". Scope: 16th to 18th Lok Sabha, the five tracked ministries (Home Affairs included). Rajya Sabha is not in the archive and was not audited.

**Update, 23 Nov 2026:** the editor approved the 124 clear misses; they are applied on the branch `home-affairs-ministry` (not deployed). Applying them moved ten MPs off the never-asked list, not eight: D Ravi Kumar (Viluppuram) and Durgadas Uikey (Betul) were missed below because the feed spells their names differently. The borderline and text-only lists remain undecided.

## Method

1. Every Road Transport & Highways question in the three Lok Sabhas was enumerated (4,961). The other four ministries were swept with 75 road-safety phrases against the archive's full text.
2. Each question was matched to the tracker by Lok Sabha, session, question number and type, with a title-and-date fallback. 838 of the tracker's 849 Lok Sabha records were found in the archive.
3. For each of the 5,513 questions the tracker does not have, the question text was read from the archive's text copy of the answer PDF, cut at the word ANSWER, so a hit means the MP raised it, not that the reply mentioned it.
4. Titles were then reviewed by hand in three passes against the approved scope.

## Results

- **Clear misses: 124.** The title is in scope under the existing rule. By ministry: Road Transport 113, Health 5, Heavy Industries 4, Urban Affairs 1, Home Affairs 1.
- **Borderline: 90**, in 11 groups, for the editor to rule on group by group.
- **Safety raised only in the question text: 313.** The title is generic (for example a highway project) but a clause asks about accidents, black spots or pedestrians. Including these would change the method from title-based to text-based.

Why the clear misses happened: the keyword list that built the baseline did not know these phrasings (cashless treatment under Road Transport, footpath, foot over bridge, driving training, fitness certificate, speed breaker, recall policy, NCAP spelled out), and its toll rule threw out "Ambulances at Toll Plazas".

## Never-asked MPs affected

Sitting Lok Sabha MPs shown as never having asked, who asked one of the clear misses (term served verified against the roster):

| MP | State | Party | Question | Date |
|---|---|---|---|---|
| Arjun Ram Meghwal | Rajasthan | BJP | Removal of Speed Breakers on NHs | 2016-05-05 |
| Arun Nehru | Tamil Nadu | DMK | Speed Monitoring on NHs | 2025-02-13 |
| Balabhadra Majhi | Odisha | BJP | Driving Training Centres | 2015-08-06 |
| Balashowry Vallabhaneni | Andhra Pradesh | JSP | Commercial Vehicles driven by LMV License holders | 2024-12-19 |
| Dhanorkar Pratibha Suresh | Maharashtra | INC | Mandatory Implementation of ADAS | 2025-12-18 |
| Mukesh Rajput | Uttar Pradesh | BJP | Driving Schools | 2021-02-11 |
| Pradan Baruah | Assam | BJP | Bharat New Car Assessment Programme | 2022-08-04 |
| Tanuj Punia | Uttar Pradesh | INC | Cameras on NHAI Roads | 2025-03-20 |

A further 9 would change only if borderline groups are accepted, and 45 more only under a text-based method.

## Clear misses

| Date | LS | Ministry | Question | Asked by |
|---|---|---|---|---|
| 2026-08-06 | LS18 | Road Transport | [Implementation of Cashless Treatment Scheme](https://elibrary.sansad.in/handle/123456789/1541732) | Iqra Choudhary |
| 2026-04-02 | LS18 | Road Transport | [Vehicle-to-Vehicle Communication System](https://elibrary.sansad.in/handle/123456789/1535595) | Adoor Prakash |
| 2026-03-12 | LS18 | Road Transport | [Automated Vehicle Testing Stations](https://elibrary.sansad.in/handle/123456789/1532313) | Brijendra Singh Ola |
| 2026-02-12 | LS18 | Road Transport | [Emergency Care Facilities on National Highways](https://elibrary.sansad.in/handle/123456789/1530784) | Magunta Sreenivasulu Reddy |
| 2026-02-12 | LS18 | Road Transport | [Rah-Veer Scheme](https://elibrary.sansad.in/handle/123456789/1530725) | G M Harish Balayogi |
| 2026-02-12 | LS18 | Road Transport | [Guidelines for Geometric Design in Hilly Terrains](https://elibrary.sansad.in/handle/123456789/1530687) | Anurag Singh Thakur |
| 2026-02-06 | LS18 | Health | [Free Treatment to Accident Victims and Cancer Patients](https://elibrary.sansad.in/handle/123456789/1529222) | Lalji Verma |
| 2026-02-05 | LS18 | Road Transport | [Implementation of Speed Management Guidelines](https://elibrary.sansad.in/handle/123456789/1528588) | Mohammad Jawed |
| 2025-12-18 | LS18 | Road Transport | [Mandatory Implementation of ADAS](https://elibrary.sansad.in/handle/123456789/1526925) | Dhanorkar Pratibha Suresh |
| 2025-08-21 | LS18 | Road Transport | [Cashless Treatment Scheme](https://elibrary.sansad.in/handle/123456789/1510981) | G Lakshminarayana, Byreddy Shabari |
| 2025-08-21 | LS18 | Road Transport | [Electronic Monitoring on NHs](https://elibrary.sansad.in/handle/123456789/1511004) | Rajkumar Chahar |
| 2025-07-31 | LS18 | Road Transport | [Deep Potholes on NH-966](https://elibrary.sansad.in/handle/123456789/1512765) | V K Sreekandan |
| 2025-04-03 | LS18 | Road Transport | [Setting up of Driving Training Centres](https://elibrary.sansad.in/handle/123456789/1517733) | Manickam Tagore B, Vijayakumar Alias Vijay Vasanth |
| 2025-03-27 | LS18 | Road Transport | [Inspections of Load and Freight-Bearing Vehicles](https://elibrary.sansad.in/handle/123456789/1523049) | Bachhav Shobha Dinesh |
| 2025-03-20 | LS18 | Road Transport | [Electronic Monitoring of National Highways](https://elibrary.sansad.in/handle/123456789/1522283) | Rajkumar Chahar |
| 2025-03-20 | LS18 | Road Transport | [Cameras on NHAI Roads](https://elibrary.sansad.in/handle/123456789/1522194) | Tanuj Punia |
| 2025-03-13 | LS18 | Road Transport | [Working Hours Limit and Rest Provisions for Drivers](https://elibrary.sansad.in/handle/123456789/1523721) | Asaduddin Owaisi |
| 2025-02-13 | LS18 | Road Transport | [Speed Monitoring on NHs](https://elibrary.sansad.in/handle/123456789/1517943) | Arun Nehru |
| 2025-02-06 | LS18 | Road Transport | [Regional Driving Training Centres](https://elibrary.sansad.in/handle/123456789/1517792) | Daggumalla Prasada Rao |
| 2025-02-06 | LS18 | Road Transport | [Reduction in Number of Blind Spots](https://elibrary.sansad.in/handle/123456789/1519589) | Ramvir Singh Bidhuri |
| 2024-12-19 | LS18 | Road Transport | [Commercial Vehicles driven by LMV License holders](https://elibrary.sansad.in/handle/123456789/1516032) | Balashowry Vallabhaneni |
| 2024-12-19 | LS18 | Road Transport | [Status of Driving Training Institutes in Andhra Pradesh](https://elibrary.sansad.in/handle/123456789/1515917) | Sribharat Mathukumilli, Appalanaidu Kalisetti, G Lakshminarayana |
| 2024-12-12 | LS18 | Road Transport | [Cashless Treatment](https://elibrary.sansad.in/handle/123456789/1514870) | Iqra Choudhary |
| 2024-12-05 | LS18 | Road Transport | [Data on Road Incidents](https://elibrary.sansad.in/handle/123456789/1513810) | Kaushalendra Kumar |
| 2024-11-28 | LS18 | Road Transport | [Foot Over Bridge in Kannur](https://elibrary.sansad.in/handle/123456789/1516946) | K Sudhakaran |
| 2024-08-01 | LS18 | Road Transport | [Renewal of Driving Licences](https://elibrary.sansad.in/handle/123456789/1317292) | Giridhari Yadav |
| 2023-12-14 | LS17 | Road Transport | [Audit of Tunnels](https://elibrary.sansad.in/handle/123456789/261221) | Sambhajirao Mane Dhairyasheel, Aparupa Poddar, Prataprao  Jadhav +3 |
| 2023-12-14 | LS17 | Road Transport | [Bharat New Car Assessment Programme](https://elibrary.sansad.in/handle/123456789/707352) | Su Thirunavukkarasar, Ravneet Singh |
| 2023-08-04 | LS17 | Health | [Financial Support for Critical Care/Emergency Centres](https://elibrary.sansad.in/handle/123456789/928891) | Rajashree Mallick |
| 2023-08-03 | LS17 | Road Transport | [Hospitals along National Highways](https://elibrary.sansad.in/handle/123456789/1422321) | Malook Nagar |
| 2023-08-03 | LS17 | Road Transport | [Lane Violations](https://elibrary.sansad.in/handle/123456789/470781) | Sunil Kumar Singh, Devji Mansingram Patel, Durga Das Uikey +5 |
| 2023-08-03 | LS17 | Road Transport | [CCTV on National Highways](https://elibrary.sansad.in/handle/123456789/788203) | Vivek Narayan Shejwalkar |
| 2023-07-27 | LS17 | Road Transport | [Regional Driving Training Centres](https://elibrary.sansad.in/handle/123456789/1422369) | Ramdas Chandrabhanji Tadas |
| 2023-03-23 | LS17 | Road Transport | [Construction of Underpasses/Foot Over Bridges on NH-44](https://elibrary.sansad.in/handle/123456789/715873) | Sanjay Bhatia |
| 2023-03-23 | LS17 | Road Transport | [Road Traffic Injuries](https://elibrary.sansad.in/handle/123456789/997081) | Sanjeev Kumar Singari |
| 2023-03-16 | LS17 | Road Transport | [Construction of Foot Over Bridge](https://elibrary.sansad.in/handle/123456789/1349757) | Sanjay Bhatia |
| 2023-02-02 | LS17 | Road Transport | [Availability of Ambulances at Toll Plazas](https://elibrary.sansad.in/handle/123456789/778838) | Ajay Kumar Mandal, Locket Chatterjee, Ramesh Chander Kaushik +1 |
| 2022-12-22 | LS17 | Road Transport | [Electronic Monitoring System on NHs](https://elibrary.sansad.in/handle/123456789/743587) | Rajkumar Chahar |
| 2022-08-05 | LS17 | Health | [Critical Care/Emergency Centres along National Highways](https://elibrary.sansad.in/handle/123456789/1479961) | Anurag Sharma |
| 2022-08-04 | LS17 | Road Transport | [Institute of Driving Training and Research](https://elibrary.sansad.in/handle/123456789/1368858) | C.N. Annadurai, Amol Ramsing Kolhe, Dhanush M. Kumar +9 |
| 2022-08-04 | LS17 | Road Transport | [Bharat New Car Assessment Programme](https://elibrary.sansad.in/handle/123456789/840163) | Pallab Lochan Das, Pradan Baruah, Sellaperumal Ramalingam |
| 2022-08-02 | LS17 | Heavy Industries | [Safety of Electric Vehicles](https://elibrary.sansad.in/handle/123456789/1298351) | Sanjay (Kaka) Ramchandra Patil |
| 2022-07-28 | LS17 | Road Transport | [Emergency Facilities on NHs](https://elibrary.sansad.in/handle/123456789/594199) | Bharati Dhirubhai Shiyal |
| 2022-07-28 | LS17 | Road Transport | [Transportation of School Children](https://elibrary.sansad.in/handle/123456789/980874) | Rajeshbhai Naranbhai Chudasama |
| 2022-07-21 | LS17 | Road Transport | [Institute of Driving Training and Research](https://elibrary.sansad.in/handle/123456789/1122558) | Sunil Kumar Soni, Arun Sao, Vijay Baghel |
| 2022-07-21 | LS17 | Road Transport | [Bharat New Car Assessment Programme](https://elibrary.sansad.in/handle/123456789/253518) | Rahul Ramesh Shewale, Chandrashekhar Sahu, Girish Bhalchandra Bapat |
| 2022-03-17 | LS17 | Road Transport | [Star Rating System for Cars](https://elibrary.sansad.in/handle/123456789/697986) | Vijayakumar (Alias) Vijay Vasanth |
| 2021-12-14 | LS17 | Heavy Industries | [Air Bags for Cars](https://elibrary.sansad.in/handle/123456789/767980) | Upendra Singh Rawat |
| 2021-07-29 | LS17 | Road Transport | [Training to Drivers](https://elibrary.sansad.in/handle/123456789/1295124) | Sudhakar Tukaram Shrangare |
| 2021-07-22 | LS17 | Road Transport | [Maintenance of Ambulances at Toll Plazas](https://elibrary.sansad.in/handle/123456789/250502) | Geeta Kora, Jugal Kishore Sharma |
| 2021-03-25 | LS17 | Road Transport | [Ambulances at Toll Plazas](https://elibrary.sansad.in/handle/123456789/1085261) | Geeta Kora, Dileshwar Kamait, Jugal Kishore Sharma |
| 2021-03-25 | LS17 | Road Transport | [Construction of Footpath along NH](https://elibrary.sansad.in/handle/123456789/551309) | Ajay Kumar Mandal |
| 2021-03-18 | LS17 | Road Transport | [Recall Policy for Vehicles](https://elibrary.sansad.in/handle/123456789/496925) | Pramod Mahajan, Gowdar Mallikarjunappa Siddeshwara |
| 2021-02-11 | LS17 | Road Transport | [Driving Schools](https://elibrary.sansad.in/handle/123456789/1437767) | Mukesh Rajput, Basanta Kumar Panda |
| 2020-09-22 | LS17 | Road Transport | [Compensation to NoKs of Migrants Died on NHsduring Lockdown](https://elibrary.sansad.in/handle/123456789/732841) | Manish Tewari |
| 2020-03-05 | LS17 | Road Transport | [Recall Policy for Vehicles](https://elibrary.sansad.in/handle/123456789/1120150) | Manoj Kishorbhai Kotak |
| 2020-02-06 | LS17 | Road Transport | [Construction of Foot Over Bridge](https://elibrary.sansad.in/handle/123456789/591996) | Darshana Vikram Jardosh |
| 2020-02-06 | LS17 | Road Transport | [Issue of Fitness Certificate for Commercial Vehicles](https://elibrary.sansad.in/handle/123456789/215950) | D. Ravikumar |
| 2020-02-06 | LS17 | Road Transport | [Implementation of Automatic Headlamp On (AHO) Rule](https://elibrary.sansad.in/handle/123456789/733003) | Raksha Nikhil Khadse |
| 2020-02-04 | LS17 | Heavy Industries | [Crash Test of Cars](https://elibrary.sansad.in/handle/123456789/286806) | Devusinh Jesingbhai Chauhan |
| 2019-12-12 | LS17 | Road Transport | [Institute of Driving Training and Research](https://elibrary.sansad.in/handle/123456789/626874) | Shyam Singh Yadav, Dhanush M. Kumar, Ganesan Selvam +1 |
| 2019-12-12 | LS17 | Road Transport | [Global New Car Assessment Programme](https://elibrary.sansad.in/handle/123456789/494943) | Devusinh Jesingbhai Chauhan |
| 2019-12-12 | LS17 | Road Transport | [Transportation of School Children](https://elibrary.sansad.in/handle/123456789/321829) | Kirron Kher |
| 2019-12-05 | LS17 | Road Transport | [Standard Brightness Level of Lights in Vehicles](https://elibrary.sansad.in/handle/123456789/837506) | Ram Swaroop Sharma |
| 2019-11-21 | LS17 | Urban Affairs | [The Delhi Cyclewalk](https://elibrary.sansad.in/handle/123456789/549782) | Sukanta Majumdar, Bhagwanth Khuba, Bhola Singh +2 |
| 2019-07-25 | LS17 | Road Transport | [Training for Safe Driving](https://elibrary.sansad.in/handle/123456789/837421) | Dhanush M. Kumar, Amol Ramsing Kolhe, Heena Vijayakumar Gavit +3 |
| 2019-07-04 | LS17 | Road Transport | [CCTV Cameras on Highways to Oversee Driving](https://elibrary.sansad.in/handle/123456789/1401155) | H. Vasanthakumar |
| 2019-07-04 | LS17 | Road Transport | [Requirement of Trained Drivers](https://elibrary.sansad.in/handle/123456789/1295523) | Rodmal Nagar, Lallu Singh, P.P. Chaudhary +2 |
| 2019-02-07 | LS16 | Road Transport | [Driving Training and Research Institutes](https://elibrary.sansad.in/handle/123456789/1222297) | Vijaysinh Mohite Patil, Dhananjay Bhimrao Mahadik, Heena Vijayakumar Gavit +3 |
| 2018-02-02 | LS16 | Health | [Road Traffic Injury Patients](https://elibrary.sansad.in/handle/123456789/1010424) | Ram Charitra |
| 2017-08-03 | LS16 | Road Transport | [Graduated Drivers Licensing System](https://elibrary.sansad.in/handle/123456789/400646) | Rabindra Kumar Jena, K. Maragatham |
| 2017-07-27 | LS16 | Road Transport | [Construction of Foot Overbridge on NH1](https://elibrary.sansad.in/handle/123456789/623194) | Ramesh Chander Kaushik |
| 2017-07-27 | LS16 | Road Transport | [Driving Competence Tests](https://elibrary.sansad.in/handle/123456789/1186008) | Kirit Premjibhai Solanki |
| 2017-07-20 | LS16 | Road Transport | [Speed Breakers](https://elibrary.sansad.in/handle/123456789/1327049) | Rajeev Shankarrao Satav, Sundar Lal Patwa |
| 2017-07-20 | LS16 | Road Transport | [Faulty Design of NHs](https://elibrary.sansad.in/handle/123456789/1151111) | Sanjay (Kaka) Ramchandra Patil |
| 2017-03-23 | LS16 | Road Transport | [Driving Discipline](https://elibrary.sansad.in/handle/123456789/763582) | Sisir Kumar Adhikari, Suresh Kodikunnil, Geetha Kothapalli |
| 2017-03-16 | LS16 | Road Transport | [Removal of Liquor Shops on NHs](https://elibrary.sansad.in/handle/123456789/798592) | P. Nagarajan, Mansukhbhai D. Vasava, Laxmi Narayan Yadav |
| 2017-03-09 | LS16 | Road Transport | [Medical Insurance to Road Users](https://elibrary.sansad.in/handle/123456789/282483) | Ram Charitra |
| 2017-03-09 | LS16 | Road Transport | [Speed on e-ways](https://elibrary.sansad.in/handle/123456789/693274) | Prem Singh Chandumajra, Chandu Barne Shrirang |
| 2017-02-09 | LS16 | Road Transport | [Underpasses, Flyovers and Foot Over Bridges](https://elibrary.sansad.in/handle/123456789/904148) | S.P. Muddahanumegowda, C.S. Puttaraju |
| 2017-02-02 | LS16 | Road Transport | [Foot Overbridges on National Highways](https://elibrary.sansad.in/handle/123456789/868759) | Prem Singh Chandumajra |
| 2016-12-15 | LS16 | Road Transport | [Rash Driving on National Highways](https://elibrary.sansad.in/handle/123456789/974309) | Anto Antony, Heena Vijayakumar Gavit, Jayakumar Jayavardhan +4 |
| 2016-12-08 | LS16 | Road Transport | [Installation of Hydraulic Gates for Speedy Rescue](https://elibrary.sansad.in/handle/123456789/1256339) | Sunil Baliram Gaikwad, Sudheer Gupta, Gajanan Chandrakant Kirtikar +4 |
| 2016-12-01 | LS16 | Road Transport | [Highway Patrol Squads](https://elibrary.sansad.in/handle/123456789/1432630) | V.Sathyabama |
| 2016-11-24 | LS16 | Road Transport | [Medical Insurance for Road Users](https://elibrary.sansad.in/handle/123456789/587350) | Jay Prakash Narayan Yadav |
| 2016-08-11 | LS16 | Road Transport | [Fitness Certificates for Vehicles](https://elibrary.sansad.in/handle/123456789/1150651) | Renuka Butta, A.T.(Nana) Patil |
| 2016-08-11 | LS16 | Road Transport | [Speed Breakers and Signages](https://elibrary.sansad.in/handle/123456789/543295) | Rekha Arun Verma |
| 2016-08-04 | LS16 | Road Transport | [Encroachment on Footpaths](https://elibrary.sansad.in/handle/123456789/1150610) | Ramachandran Mullappally |
| 2016-07-28 | LS16 | Road Transport | [Fake Licences](https://elibrary.sansad.in/handle/123456789/211053) | Dushyant Chautala |
| 2016-07-28 | LS16 | Road Transport | [Medical Care Facilities on NHs](https://elibrary.sansad.in/handle/123456789/487318) | P.K. Shreemathi Teacher |
| 2016-07-28 | LS16 | Road Transport | [Anti-Lock Braking System](https://elibrary.sansad.in/handle/123456789/939055) | Bhuwan Chandra Khanduri |
| 2016-07-21 | LS16 | Road Transport | [Removal of Liquor Shops on NHs](https://elibrary.sansad.in/handle/123456789/798170) | Manoj Rajoria |
| 2016-05-05 | LS16 | Road Transport | [Fitness and Pollution Centres](https://elibrary.sansad.in/handle/123456789/868367) | Ponnusamy Venugopal |
| 2016-05-05 | LS16 | Road Transport | [Removal of Speed Breakers on NHs](https://elibrary.sansad.in/handle/123456789/1255968) | K. Ashok Kumar, P.P. Chaudhary, Sudheer Gupta +13 |
| 2016-05-05 | LS16 | Road Transport | [Safe Traffic System Design](https://elibrary.sansad.in/handle/123456789/973937) | P.K. Biju |
| 2016-04-28 | LS16 | Road Transport | [Driving-cum-Fitness Training Centres](https://elibrary.sansad.in/handle/123456789/692776) | C.R. Chaudhary, Hariom Singh Rathore |
| 2016-04-28 | LS16 | Road Transport | [Graduated Drivers' Licensing System (GDLS)](https://elibrary.sansad.in/handle/123456789/868321) | Rabindra Kumar Jena |
| 2016-04-28 | LS16 | Road Transport | [Lane System for Traffic](https://elibrary.sansad.in/handle/123456789/692775) | P.P. Chaudhary |
| 2016-03-10 | LS16 | Road Transport | [Star Ratings for Vehicles](https://elibrary.sansad.in/handle/123456789/586983) | G. Hari, Vijaysinh Mohite Patil, T. Radhakrishnan |
| 2016-03-03 | LS16 | Road Transport | [Strict Provisions for Offenders](https://elibrary.sansad.in/handle/123456789/246470) | K. Ashok Kumar |
| 2016-03-03 | LS16 | Road Transport | [Fine on Rule's Violators](https://elibrary.sansad.in/handle/123456789/1044434) | Om Birla, Chandu Lal Sahu |
| 2016-02-25 | LS16 | Road Transport | [Potholes on National Highways](https://elibrary.sansad.in/handle/123456789/868168) | Ram Charitra |
| 2016-02-25 | LS16 | Road Transport | [Installation of Video Cameras and Black Box for Commercial Vehicles](https://elibrary.sansad.in/handle/123456789/1079762) | Nityanand Rai |
| 2016-02-25 | LS16 | Road Transport | [Provision of CCTV Cameras on National Highways](https://elibrary.sansad.in/handle/123456789/396973) | Sushil Kumar Singh |
| 2015-12-17 | LS16 | Road Transport | [Building of Footpath along Highways](https://elibrary.sansad.in/handle/123456789/938703) | Meenakshi Lekhi, Vinayak Bhaurao Raut, Rahul Ramesh Shewale +1 |
| 2015-12-10 | LS16 | Road Transport | [Capping of Third Party Insurance Claims](https://elibrary.sansad.in/handle/123456789/246319) | A.T.(Nana) Patil, A.P. Jithender Reddy |
| 2015-12-08 | LS16 | Heavy Industries | [Recall of Faulty Vehicles](https://elibrary.sansad.in/handle/123456789/1220225) | K.R.P. Prabhakaran |
| 2015-12-03 | LS16 | Road Transport | [NRSTMB](https://elibrary.sansad.in/handle/123456789/542385) | Kamal Nath, Nanabhau Falgunrao Patole, Jyotiraditya Madhavrao Scindia +1 |
| 2015-12-03 | LS16 | Road Transport | [Signboards](https://elibrary.sansad.in/handle/123456789/762729) | R. Gopalakrishnan, Ramesh Chander Kaushik |
| 2015-08-13 | LS16 | Road Transport | [Cashless Treatment](https://elibrary.sansad.in/handle/123456789/542305) | Ashok Shankarrao Chavan, Sunil Baliram Gaikwad, Sudheer Gupta +3 |
| 2015-08-13 | LS16 | Road Transport | [Speed Breakers](https://elibrary.sansad.in/handle/123456789/542307) | Bharati Dhirubhai Shiyal |
| 2015-08-13 | LS16 | Road Transport | [Rules for Traffic Violators](https://elibrary.sansad.in/handle/123456789/542308) | Ch. Malla Reddy, Sundar Lal Patwa |
| 2015-08-13 | LS16 | Road Transport | [RADMS](https://elibrary.sansad.in/handle/123456789/797733) | R.K. Bharathi Mohan |
| 2015-08-06 | LS16 | Road Transport | [Driving Training Centres](https://elibrary.sansad.in/handle/123456789/762633) | Balabhadra Majhi |
| 2015-08-06 | LS16 | Road Transport | [Driving Training Institutes in Odisha](https://elibrary.sansad.in/handle/123456789/246151) | Baijayant  Jay  Panda |
| 2015-04-23 | LS16 | Road Transport | [BAN ON LIQUOR ON NHS](https://elibrary.sansad.in/handle/123456789/1431770) | Santosh Ahlawat, A. Arunmozhithevan, Suresh Kodikunnil +3 |
| 2015-03-17 | LS16 | Home Affairs | [PROTECTION OF BYSTANDERS](https://elibrary.sansad.in/handle/123456789/762444) | Santosh Ahlawat |
| 2015-03-05 | LS16 | Road Transport | [FOG WARNING SYSTEM AT HIGHWAYS](https://elibrary.sansad.in/handle/123456789/541903) | Ashok Shankarrao Chavan, Sudheer Gupta, Gajanan Chandrakant Kirtikar +1 |
| 2015-02-26 | LS16 | Road Transport | [MEDICAL SERVICES AT NATIONL HIGHWAYS](https://elibrary.sansad.in/handle/123456789/316636) | B.V. Nayak, Jagdambika Pal, Mekapati Rajamohan Reddy +1 |
| 2015-02-26 | LS16 | Road Transport | [FITNESS OF VEHICLES](https://elibrary.sansad.in/handle/123456789/762318) | Ponguleti Srinivasa Reddy |
| 2015-02-26 | LS16 | Road Transport | [HIGHWAY POLICING](https://elibrary.sansad.in/handle/123456789/1290493) | P. Kumar |
| 2014-12-19 | LS16 | Health | [TREATMENT TO ROAD ACCIDENT VICTIMS AND WOMEN IN LABOUR](https://elibrary.sansad.in/handle/123456789/1184455) | Ashok Shankarrao Chavan |
| 2014-12-18 | LS16 | Road Transport | [BAN ON USE OF EARPHONE WHILE WALKING](https://elibrary.sansad.in/handle/123456789/1221348) | Sunil Baliram Gaikwad |
| 2014-08-14 | LS16 | Road Transport | [HIGHWAY PATROLLING](https://elibrary.sansad.in/handle/123456789/1115635) | Mamtaz Sanghamita |

## Borderline, by group

### Traffic management and ITS systems (7)

| Date | LS | Ministry | Question | Asked by |
|---|---|---|---|---|
| 2026-03-19 | LS18 | Road Transport | [Deployment of AI-Based Traffic Management Systems](https://elibrary.sansad.in/handle/123456789/1533663) | Roopkumari Choudhary |
| 2026-02-12 | LS18 | Road Transport | [Advanced Traffic Management Systems](https://elibrary.sansad.in/handle/123456789/1530657) | Narayan Tatu Rane |
| 2025-07-24 | LS18 | Road Transport | [Intelligent Transportation System on Highways](https://elibrary.sansad.in/handle/123456789/1511538) | Arun Bharti |
| 2024-12-05 | LS18 | Road Transport | [Intelligent Transport Systems](https://elibrary.sansad.in/handle/123456789/1513686) | K Radhakrishnan |
| 2023-12-07 | LS17 | Road Transport | [Advance Traffic Management System](https://elibrary.sansad.in/handle/123456789/953548) | Sangamlal Kadedin Gupta, Anurag Sharma, C. R. Patil +3 |
| 2022-07-28 | LS17 | Road Transport | [Intelligent Transport System](https://elibrary.sansad.in/handle/123456789/980875) | Prataprao Ganpatrao Jadhav, Bidyut Baran Mahato, Manoj Kumar Tiwari +8 |
| 2015-12-10 | LS16 | Road Transport | [Traffic Management System](https://elibrary.sansad.in/handle/123456789/281738) | R. Parthipan |

### Highway helplines and incident services (5)

| Date | LS | Ministry | Question | Asked by |
|---|---|---|---|---|
| 2019-07-18 | LS17 | Road Transport | [Phone Helpline Facility along NHs](https://elibrary.sansad.in/handle/123456789/250758) | Shivkumar Chanabasappa Udasi |
| 2016-12-08 | LS16 | Road Transport | [Phone Helpline on National Highways](https://elibrary.sansad.in/handle/123456789/246925) | Kinjarapu Ram Mohan Naidu |
| 2016-11-17 | LS16 | Road Transport | [Highway incident and Allied Services Scheme](https://elibrary.sansad.in/handle/123456789/622648) | Gaurav Gogoi, Jyotiraditya Madhavrao Scindia |
| 2016-03-03 | LS16 | Road Transport | [Phone Helpline on NHs](https://elibrary.sansad.in/handle/123456789/1115185) | Jagdambika Pal |
| 2015-02-26 | LS16 | Road Transport | [HELPLINE NUMBER ON HIGHWAYS](https://elibrary.sansad.in/handle/123456789/938228) | Vinayak Bhaurao Raut, Rahul Ramesh Shewale |

### Street lighting on highways (12)

| Date | LS | Ministry | Question | Asked by |
|---|---|---|---|---|
| 2025-12-18 | LS18 | Road Transport | [Street Lights on National Highways in West Bengal](https://elibrary.sansad.in/handle/123456789/1526898) | Khalilur Rahaman |
| 2025-07-24 | LS18 | Road Transport | [Street Lighting on NH-966A](https://elibrary.sansad.in/handle/123456789/1511583) | Hibi Eden |
| 2023-12-21 | LS17 | Road Transport | [Lighting System on National Highways](https://elibrary.sansad.in/handle/123456789/261411) | Shriniwas Dadasaheb Patil, Bhola Singh, Jayanta Kumar Roy +4 |
| 2023-08-10 | LS17 | Road Transport | [Street Lights on Highways](https://elibrary.sansad.in/handle/123456789/527788) | Hibi Eden |
| 2023-03-16 | LS17 | Road Transport | [Arrangement of Lights on Delhi Roads](https://elibrary.sansad.in/handle/123456789/750838) | Janardan Singh Sigriwal |
| 2022-12-22 | LS17 | Road Transport | [High-mast Lighting on NH-44](https://elibrary.sansad.in/handle/123456789/813739) | A.K.P. Chinraj |
| 2022-08-04 | LS17 | Road Transport | [Lighting System on National Highways](https://elibrary.sansad.in/handle/123456789/1368857) | Supriya Sule, Amol Ramsing Kolhe, DNV Senthilkumar S. +3 |
| 2021-12-09 | LS17 | Road Transport | [Lighting System on National Highways](https://elibrary.sansad.in/handle/123456789/495772) | Prataprao Ganpatrao Jadhav, Bidyut Baran Mahato, Ravindra Kushawaha +5 |
| 2020-02-06 | LS17 | Road Transport | [LED Lighting on NHs in Tamil Nadu](https://elibrary.sansad.in/handle/123456789/697736) | T. Sumathy (A) Thamizhachi Thangapandian |
| 2018-12-13 | LS16 | Road Transport | [Lighting on National Highways](https://elibrary.sansad.in/handle/123456789/588886) | Anirudhan Sampath |
| 2017-08-10 | LS16 | Road Transport | [LED Lights on NHs](https://elibrary.sansad.in/handle/123456789/1397783) | Sanganna Amarappa Karadi |
| 2017-04-06 | LS16 | Road Transport | [Lighting on NHs](https://elibrary.sansad.in/handle/123456789/1080563) | Elumalai Vallaigounder |

### Driver qualification rules (3)

| Date | LS | Ministry | Question | Asked by |
|---|---|---|---|---|
| 2019-07-18 | LS17 | Road Transport | [Minimum Qualification for Drivers](https://elibrary.sansad.in/handle/123456789/1154704) | Syed Imtiaz Jaleel, Asaduddin Owaisi |
| 2017-08-10 | LS16 | Road Transport | [Educational Qualification for Drivers](https://elibrary.sansad.in/handle/123456789/1045338) | Nanabhau Falgunrao Patole |
| 2017-03-09 | LS16 | Road Transport | [Educational Qualification for Public Transport Drivers](https://elibrary.sansad.in/handle/123456789/1362335) | K. Maragatham |

### Third-party motor insurance (2)

| Date | LS | Ministry | Question | Asked by |
|---|---|---|---|---|
| 2015-08-06 | LS16 | Road Transport | [Third Party Insurance](https://elibrary.sansad.in/handle/123456789/1079517) | Abhishek Banerjee, Heena Vijayakumar Gavit, Kirron Kher +4 |
| 2015-04-30 | LS16 | Road Transport | [THIRD PARTY MOTOR INSURANCE](https://elibrary.sansad.in/handle/123456789/210382) | Kotha Prabhakar Reddy |

### Electric-vehicle fires (Heavy Industries) (6)

| Date | LS | Ministry | Question | Asked by |
|---|---|---|---|---|
| 2025-03-18 | LS18 | Heavy Industries | [Fire accidents caused by EVs](https://elibrary.sansad.in/handle/123456789/1521754) | Kirsan Namdeo |
| 2023-12-12 | LS17 | Heavy Industries | [Incidents of Fire in Electric Vehicles](https://elibrary.sansad.in/handle/123456789/742505) | Hibi Eden |
| 2023-08-01 | LS17 | Heavy Industries | [Fire Incidents in Electric Vehicles](https://elibrary.sansad.in/handle/123456789/470788) | Bhartruhari Mahtab |
| 2023-03-28 | LS17 | Heavy Industries | [Incidents of Fire in Electric Vehicles](https://elibrary.sansad.in/handle/123456789/891479) | Thirumaavalavan Tholkappiyan |
| 2022-12-20 | LS17 | Heavy Industries | [Incidents of Fire in Electric Vehicles](https://elibrary.sansad.in/handle/123456789/297765) | P. Velusamy |
| 2022-07-19 | LS17 | Heavy Industries | [Incidents of Fire in Electric Vehicles](https://elibrary.sansad.in/handle/123456789/1016302) | Sukanta Majumdar, Bhola Singh, Jayanta Kumar Roy +8 |

### Emergency care and EMS (Health) (4)

| Date | LS | Ministry | Question | Asked by |
|---|---|---|---|---|
| 2024-07-26 | LS18 | Health | [National Emergency Life Support Skill Centres](https://elibrary.sansad.in/handle/123456789/648504) | Prabhakar Reddy Vemireddy |
| 2023-12-15 | LS17 | Health | [Emergency Health Care Facilities](https://elibrary.sansad.in/handle/123456789/777783) | Vijay Kumar Dubey |
| 2023-12-15 | LS17 | Health | [Streamlining Emergency Response System](https://elibrary.sansad.in/handle/123456789/812835) | Sangeeta Azad |
| 2015-02-27 | LS16 | Health | [UNIVERSAL NO. FOR MEDICAL EMERGENCY](https://elibrary.sansad.in/handle/123456789/1255213) | Kirron Kher |

### Bridge and tunnel collapses, structural defects (19)

| Date | LS | Ministry | Question | Asked by |
|---|---|---|---|---|
| 2026-03-19 | LS18 | Road Transport | [Major Deficiencies on National Highways](https://elibrary.sansad.in/handle/123456789/1533706) | Abu Taher Khan |
| 2026-03-12 | LS18 | Road Transport | [Deficiencies on National Highways](https://elibrary.sansad.in/handle/123456789/1532366) | Jagadish Chandra Barma Basunia |
| 2025-08-21 | LS18 | Road Transport | [Structural Issues of NHs](https://elibrary.sansad.in/handle/123456789/1511031) | Balwant Baswant Wankhade |
| 2025-08-21 | LS18 | Road Transport | [Faulty Construction on NH 752E/561A](https://elibrary.sansad.in/handle/123456789/1511049) | Bajrang Manohar Sonwane |
| 2025-07-24 | LS18 | Road Transport | [Iron Bridge Collapse in Pune](https://elibrary.sansad.in/handle/123456789/1511628) | Bachhav Shobha Dinesh |
| 2024-12-05 | LS18 | Road Transport | [Technical Flaws in Delhi-Mumbai Expressway](https://elibrary.sansad.in/handle/123456789/1517330) | Hanuman Beniwal |
| 2024-08-08 | LS18 | Road Transport | [Collapse of Silkyara Tunnel](https://elibrary.sansad.in/handle/123456789/789180) | Karti P Chidambaram, Shafi Parambil |
| 2024-07-25 | LS18 | Road Transport | [Bridge Collapse on NH](https://elibrary.sansad.in/handle/123456789/964888) | Amol Ramsing Kolhe, Supriya Sule, Sanjay Dina Patil +6 |
| 2024-07-25 | LS18 | Road Transport | [Silkyara Tunnel Collapse in Uttarakhand](https://elibrary.sansad.in/handle/123456789/613282) | Sudama Prasad |
| 2023-12-14 | LS17 | Road Transport | [Collapse of Bridge](https://elibrary.sansad.in/handle/123456789/812615) | Mohammad Jawed |
| 2023-12-07 | LS17 | Road Transport | [Collapsed Tunnel](https://elibrary.sansad.in/handle/123456789/1447015) | K. Subbarayan, T. R. Paarivendhar |
| 2023-08-10 | LS17 | Road Transport | [Collapsed Flyover](https://elibrary.sansad.in/handle/123456789/1210465) | T. R. Paarivendhar, Muniyan Selvaraj |
| 2023-07-27 | LS17 | Road Transport | [Bridge Collapse on NH](https://elibrary.sansad.in/handle/123456789/272116) | Rakesh Singh |
| 2022-12-22 | LS17 | Road Transport | [Defects in NHs](https://elibrary.sansad.in/handle/123456789/954575) | P. C. Mohan |
| 2020-09-22 | LS17 | Road Transport | [Collapse of Bridge in Kerala](https://elibrary.sansad.in/handle/123456789/697578) | K. Muraleedharan |
| 2020-09-17 | LS17 | Road Transport | [Incidents of Bridge Collapse](https://elibrary.sansad.in/handle/123456789/1296008) | M. K. Raghavan |
| 2019-07-11 | LS17 | Road Transport | [Deficiencies in National Highways](https://elibrary.sansad.in/handle/123456789/802394) | H. Vasanthakumar |
| 2016-12-01 | LS16 | Road Transport | [Collapse of Bridge on Mumbai-Goa Highway](https://elibrary.sansad.in/handle/123456789/904015) | Gaurav Gogoi, Jyotiraditya Madhavrao Scindia |
| 2016-04-28 | LS16 | Road Transport | [Defects in NHs](https://elibrary.sansad.in/handle/123456789/487064) | Devajibhai Govindbhai Fatepara |

### Medians, dividers and rail crossings (4)

| Date | LS | Ministry | Question | Asked by |
|---|---|---|---|---|
| 2021-12-09 | LS17 | Road Transport | [Construction of Divider on NH-35](https://elibrary.sansad.in/handle/123456789/803106) | R.K. Singh Patel |
| 2021-07-22 | LS17 | Road Transport | [Median Cut on NH-27](https://elibrary.sansad.in/handle/123456789/907726) | Devji Patel |
| 2017-07-27 | LS16 | Road Transport | [Cuts on Medians](https://elibrary.sansad.in/handle/123456789/833823) | Mekapati Rajamohan Reddy |
| 2017-03-30 | LS16 | Road Transport | [Railway Crossings on National Highways](https://elibrary.sansad.in/handle/123456789/488050) | Prataprao Ganpatrao Jadhav, Chandrakant Bhaurao Khaire |

### Encroachment on highways (9)

| Date | LS | Ministry | Question | Asked by |
|---|---|---|---|---|
| 2025-07-24 | LS18 | Road Transport | [Preventing Encroachment on National Highways](https://elibrary.sansad.in/handle/123456789/1511630) | Rahul Kaswan |
| 2024-11-28 | LS18 | Road Transport | [Illegal Encroachment on NHs](https://elibrary.sansad.in/handle/123456789/1516973) | Rajiv Pratap Rudy |
| 2023-08-10 | LS17 | Road Transport | [Encroachment of NHs](https://elibrary.sansad.in/handle/123456789/307292) | Sri Krishna Devarayalu Lavu |
| 2023-07-20 | LS17 | Road Transport | [Encroachment on Highways](https://elibrary.sansad.in/handle/123456789/1034662) | Dileshwar Kamait |
| 2023-02-02 | LS17 | Road Transport | [Encroachment along NHs](https://elibrary.sansad.in/handle/123456789/673347) | Dipsinh Shankarsinh Rathod, Mohanbhai Kalyanji Kundariya |
| 2022-12-15 | LS17 | Road Transport | [Removal of Encroachment from NHs](https://elibrary.sansad.in/handle/123456789/1236327) | Janardan Singh Sigriwal |
| 2015-03-05 | LS16 | Road Transport | [ENCROACHMENT ON NATIONAL HIGHWAYS](https://elibrary.sansad.in/handle/123456789/692226) | Hukum Singh |
| 2014-07-31 | LS16 | Road Transport | [ENCROACHMENT ON NHS](https://elibrary.sansad.in/handle/123456789/1397243) | Ashok Mahadeorao Nete |
| 2014-07-17 | LS16 | Road Transport | [ENCROACHMENT OF GT ROAD](https://elibrary.sansad.in/handle/123456789/1043801) | Om Prakash Yadav |

### Other single questions (19)

| Date | LS | Ministry | Question | Asked by |
|---|---|---|---|---|
| 2026-03-19 | LS18 | Urban Affairs | [Walk to Work Projects](https://elibrary.sansad.in/handle/123456789/1533508) | Tangella Uday Srinivas |
| 2026-02-05 | LS18 | Road Transport | [National Design Standards for Trucks](https://elibrary.sansad.in/handle/123456789/1528493) | Rahul Kaswan |
| 2024-08-01 | LS18 | Road Transport | [National policy on Traffic Management for Critical Services](https://elibrary.sansad.in/handle/123456789/964822) | Yogender Chandolia |
| 2023-02-02 | LS17 | Urban Affairs | [Accidents due to Neglected Drains](https://elibrary.sansad.in/handle/123456789/848873) | Su Thirunavukkarasar, Ravneet Singh |
| 2021-07-29 | LS17 | Road Transport | [Norms for Public Transport Vehicles](https://elibrary.sansad.in/handle/123456789/321154) | Ashok Mahadeorao Nete |
| 2020-03-12 | LS17 | Road Transport | [Security for Women in Public Road Transport](https://elibrary.sansad.in/handle/123456789/1120148) | Meenakshi Lekhi, P.C. Gaddigoudar |
| 2019-11-21 | LS17 | Road Transport | [Use of Nitrogen in Tyre](https://elibrary.sansad.in/handle/123456789/662110) | Mala Roy |
| 2019-06-27 | LS17 | Road Transport | [Violation of Law by Ola and Uber Drivers](https://elibrary.sansad.in/handle/123456789/250842) | Jagdambika Pal |
| 2019-06-27 | LS17 | Road Transport | [Passenger Security in Auto/Taxi](https://elibrary.sansad.in/handle/123456789/837418) | Vinayak Bhaurao Raut |
| 2019-02-12 | LS16 | Home Affairs | [Deaths on Road Construction Sites](https://elibrary.sansad.in/handle/123456789/212700) | Kaushal Kishore |
| 2018-12-13 | LS16 | Road Transport | [Rules for Black Film and Bumper Guard](https://elibrary.sansad.in/handle/123456789/588889) | Kaushal Kishore |
| 2017-08-10 | LS16 | Road Transport | [Tubeless Tyres in Buses](https://elibrary.sansad.in/handle/123456789/1080771) | Ravindra Kumar Ray |
| 2017-07-20 | LS16 | Road Transport | [Opening of Liquor Shops](https://elibrary.sansad.in/handle/123456789/1009785) | Saugata Roy |
| 2016-08-02 | LS16 | Heavy Industries | [Testing Centres for Vehicles](https://elibrary.sansad.in/handle/123456789/939079) | Rabindra Kumar Jena |
| 2016-03-10 | LS16 | Road Transport | [Traffic Norms](https://elibrary.sansad.in/handle/123456789/797991) | Jose K. Mani |
| 2015-12-17 | LS16 | Road Transport | [Separate Lane for Emergency Vehicles](https://elibrary.sansad.in/handle/123456789/657331) | Vinayak Bhaurao Raut, Rahul Ramesh Shewale, Shrikant Eknath Shinde |
| 2015-04-28 | LS16 | Heavy Industries | [FAULTY CNG KITS](https://elibrary.sansad.in/handle/123456789/542103) | Kanwar Singh Tanwar |
| 2014-12-11 | LS16 | Road Transport | [TRAINING ON TRAFFIC MANAGEMENT](https://elibrary.sansad.in/handle/123456789/1256895) | P. Nagarajan |
| 2014-12-04 | LS16 | Road Transport | [SUN CONTROL FILM FOR VEHICLES](https://elibrary.sansad.in/handle/123456789/658493) | E.T. Mohammad Bashir, Chandrakant Bhaurao Khaire, Anoop Mishra |

## Limits

- Lok Sabha only. The Rajya Sabha half of the tracker (688 records) has had no equivalent audit.
- The archive leaves the ministry blank for some 16th Lok Sabha records in sessions XIII to XV; these were resolved from the question text where possible, 16 could not be.
- The title review was by hand across about 1,500 titles picked by vocabulary; roughly 4,000 remaining titles (plain construction, funding and health titles) were not read one by one.
- Answer PDF links are not in this file; they come from Parliament's question API when records are applied.
