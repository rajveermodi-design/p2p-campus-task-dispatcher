# CAMPUS RUNNER: PEER-TO-PEER CAMPUS TASK DISPATCHER
## A Secure, Community-Driven Micro-Errand & Task Exchange Platform for University Campuses

---

**Course / Project Title:** Capstone / Mini-Project Report  
**Submitted By:**  
- **Name:** Rajveer Modi  
- **Registration Number:** (Enter Your Reg No here, e.g., 21BCEXXXX)  
- **Email:** rajveer.modi2025@vitstudent.ac.in  
- **Department:** Department of Computer Science and Engineering  
- **Institution:** Vellore Institute of Technology (VIT), Vellore  

**Faculty Guide / Evaluator:**  
- **Professor / Reviewer Name:** [Faculty Name Placeholder]  
- **Designation:** Department of Computer Science and Engineering  

**Academic Year:** 2025 – 2026  

---

## ACKNOWLEDGEMENT

I would like to express my sincere gratitude to my faculty guide and the Department of Computer Science and Engineering at Vellore Institute of Technology for providing the guidance, facilities, and academic encouragement necessary to complete this project.

I am also thankful to my peers and fellow hostel-mates whose everyday campus challenges inspired the motivation and feature set of this application.

---

## ABSTRACT

In large university campuses with tens of thousands of residential students, daily micro-errands—such as urgent assignment printouts, lab component pickups, stationary purchases, and cafeteria parcels—often cause considerable loss of study time and personal productivity. While commercial delivery apps (Swiggy, Zomato, Dunzo) exist outside the campus, they cannot enter hostel blocks, cannot access restricted academic buildings or labs, and have minimum order limits that make small errands unaffordable. Consequently, students rely on informal WhatsApp or Telegram groups, which are chaotic, prone to forgotten requests, and carry financial risks like unpaid runners or disputed payments.

To address this gap, **Campus Runner** is designed as a centralized, secure, peer-to-peer (P2P) task dispatch platform tailored specifically for college campuses. It enables students who need an errand done (**Requesters**) to post tasks with a specific monetary reward (**Bounty**), while students who are already near that location (**Runners**) can place bids to fulfill it. 

To eliminate payment fraud without needing complex payment gateways, the system introduces:
1. **In-App Wallet with Escrow Protection:** When an errand is created, the bounty is held safely in escrow. The requester cannot cancel and run away with the money while the runner is delivering, nor is the money released until the task is verified.
2. **Mutual Secret PIN Verification:** A secret 4-digit verification code is given only to the requester. When the runner physically hands over the item, the requester shares the PIN. Entering the correct PIN instantly closes the task and transfers the money to the runner's wallet.
3. **Campus Trust & Reputation System:** Runners build a verified rating based on completed errands, encouraging reliable and timely service.

Built with a modern **FastAPI** Python backend, a clean **MySQL** database, and an intuitive, responsive web frontend, the project demonstrates how database safety and clean software design can solve practical, day-to-day problems in student campus life.

---

## TABLE OF CONTENTS

1. [Introduction & Motivation](#1-introduction--motivation)
2. [Problem Statement & Objectives](#2-problem-statement--objectives)
3. [Proposed Solution: How Campus Runner Works](#3-proposed-solution-how-campus-runner-works)
4. [Key Features & Modules](#4-key-features--modules)
5. [System Architecture & Technology Stack](#5-system-architecture--technology-stack)
6. [Database Design & Key Tables](#6-database-design--key-tables)
7. [Safety & Fairness Mechanisms](#7-safety--fairness-mechanisms)
8. [Step-by-Step User Journey: A Real-Life Example](#8-step-by-step-user-journey-a-real-life-example)
9. [Testing & Functional Verification](#9-testing--functional-verification)
10. [Challenges Faced & Solutions](#10-challenges-faced--solutions)
11. [Limitations & Future Enhancements](#11-limitations--future-enhancements)
12. [Conclusion & Key Learnings](#12-conclusion--key-learnings)
13. [References](#13-references)

---

## 1. INTRODUCTION & MOTIVATION

Life inside a large university campus is fast-paced. Students often find themselves in situations where they urgently need an errand completed, but cannot leave their current location:
- An engineering student in a software lab 2 kilometers away urgently needs a 10-page report printed before a 2:00 PM deadline.
- A student sick in their hostel room needs medicine from the campus health center or pharmacy.
- A team preparing for an evening hackathon needs hardware sensors or cables from an electronics lab across campus.
- A student studying for semester exams in the library wants a canteen snack or notebook without losing their study desk.

At the same time, at any given moment, dozens of other students are **already walking past the library, waiting at the campus Xerox shop, or sitting at the food court**. These students would happily pick up a printout or grab an item for a peer in exchange for a small bounty of ₹30 to ₹80.

Currently, students attempt to coordinate this using informal WhatsApp or Telegram batches:
```
[WhatsApp Group Message]
"Hey guys! Anyone near TT Xerox shop right now? Need 5 prints urgently! Will GPay ₹50."
```

While this informal system works occasionally, it suffers from severe limitations:
- **Messages get buried** under hundreds of chat texts.
- **No confirmation:** Two people might both buy the item, causing confusion and wasted money.
- **Payment default:** Sometimes the requester forgets to pay or delays UPI payment indefinitely.
- **No accountability:** A runner might accept the task and then disappear, leaving the requester stranded right before a deadline.

**Campus Runner** solves these challenges by transforming random chat messages into a dedicated, organized, and fair peer-to-peer campus task marketplace.

---

## 2. PROBLEM STATEMENT & OBJECTIVES

### 2.1 Problem Statement
"Campus students lack a reliable, structured, and financially secure platform to request and fulfill localized physical errands within university premises, leading to lost time, communication overhead, and frequent payment friction."

### 2.2 Project Objectives
1. **Develop an Easy-to-Use Web Platform:** Provide an intuitive interface where students can switch seamlessly between posting errands (**Requester**) and accepting tasks (**Runner**).
2. **Implement Safe In-App Wallet & Escrow:** Ensure that money is never lost or stolen. Bounties must be locked before an errand starts and automatically transferred upon successful delivery.
3. **Prevent Fraud with Physical Handover PINs:** Implement a two-factor physical verification mechanism so that payment can only be released when the requester has physically received the item.
4. **Build a Transparent Bidding Engine:** Allow multiple prospective runners to submit their expected delivery time and quotes, letting the requester select the best student for the job.
5. **Ensure Reliable Performance:** Design the system with a structured database so that data stays consistent even when multiple students bid on or accept an errand at the exact same second.

---

## 3. PROPOSED SOLUTION: HOW CAMPUS RUNNER WORKS

Campus Runner operates on a clean, cyclical workflow designed around student safety and simplicity.

```
+--------------------------------------------------------------------------+
|                        CAMPUS RUNNER WORKFLOW                            |
+--------------------------------------------------------------------------+

   [1. POST ERRAND]
   Requester enters errand details (Pickup, Drop, Bounty, Notes).
   System verifies wallet balance and locks Bounty in ESCROW.
            |
            v
   [2. RUNNER BIDDING]
   Task appears on the Live Campus Feed.
   Runners in that area view the errand and submit their Bids with estimated times.
            |
            v
   [3. 1-CLICK ASSIGNMENT]
   Requester reviews bids (checking Runner trust rating & delivery time).
   Requester clicks "Assign" -> Task state becomes 'in_transit'.
   A secret 4-digit PIN is generated and visible ONLY to the Requester.
            |
            v
   [4. PHYSICAL ERRAND & DELIVERY]
   Runner collects the item and arrives at the requester's drop location.
   Runner hands over the parcel/document to the Requester.
            |
            v
   [5. PIN VERIFICATION & INSTANT PAYOUT]
   Requester shares the 4-digit PIN with the Runner.
   Runner enters PIN in the web app.
   System validates PIN -> Escrow is released -> Runner's wallet is credited!
```

---

## 4. KEY FEATURES & MODULES

### 4.1 Unified Student Profiles & Quick Role Switching
- Students log in using their institutional email ID and registration number.
- Any student can be a **Requester** in the morning and a **Runner** in the evening. There is no need for two separate apps.
- A quick-switch toggle allows users to view the platform from either perspective with a single click.

### 4.2 In-App Wallet with Escrow Protection
- Every student has an in-app campus wallet.
- Students can top up their wallet balance (simulated or via payment integration).
- When an errand is created, the bounty amount is automatically deducted from the requester’s available balance and stored in a secure **Escrow** state.
- If no runner accepts the task and the requester cancels it, the escrowed money is refunded immediately to the requester's balance.

### 4.3 Live Errand Marketplace Feed
- Errand listings show:
  - Task Title and Category (Printout, Canteen, Lab Delivery, Stationary)
  - Pickup Location (e.g., *Main Library Xerox, Ground Floor*)
  - Drop Location (e.g., *Hostel Block D, Room 412*)
  - Bounty Amount (e.g., *₹60.00*)
  - Current Status (*Open*, *Assigned*, *In-Transit*, *Completed*)
- Clean visual status badges keep everyone on the same page.

### 4.4 Competitive Bidding & Selection
- Multiple runners can place a bid on an open errand.
- Bids include the runner's name, current trust rating (e.g., 4.9 ★), and estimated completion time (e.g., 15 mins).
- The requester reviews the offers and picks the most suitable runner.
- When an assignment is confirmed, all competing bids are automatically marked as rejected, ensuring clarity.

### 4.5 Secret 4-Digit Handover PIN
- To prevent a runner from marking a task as "complete" without actually delivering the item, the system generates a random 4-digit PIN code upon assignment.
- This PIN is shown **only** on the requester's private task card.
- The runner must ask the requester for the PIN upon handing over the parcel in person.
- Once entered, the database verifies the token, marks the task `completed`, and instantly credits the runner's wallet.

### 4.6 Trust & Rating System
- Upon successful delivery, requesters can rate their experience from 1 to 5 stars.
- High-performing runners build an excellent reputation, making them more likely to be selected for future high-bounty errands.

---

## 5. SYSTEM ARCHITECTURE & TECHNOLOGY STACK

The project is structured using a standard **3-Tier Architecture**, ensuring clear separation between the user interface, business logic, and data storage.

```
+--------------------------------------------------------------------------+
|                         SYSTEM ARCHITECTURE                              |
+--------------------------------------------------------------------------+

  [ TIER 1: FRONTEND (Client Layer) ]
  * HTML5, CSS3, Vanilla Modern JavaScript
  * Responsive cards, modal dialogues, live state toggling
  * Runs directly in any mobile or desktop browser without app installation
             |
             | REST API / JSON over HTTP
             v
  [ TIER 2: BACKEND (FastAPI ASGI Engine) ]
  * Python 3.10+ with FastAPI Framework
  * Fast, lightweight asynchronous request handling
  * Pydantic data validation schemas for clean error messages
  * SQLAlchemy ORM for clean database query management
             |
             | MySQL TCP Connection Pool (PyMySQL)
             v
  [ TIER 3: PERSISTENCE (MySQL Database) ]
  * MySQL 8.0 Relational Database Engine
  * Tables for Students, Tasks, Bids, and Escrow Transactions
  * Row-level locking & active triggers to protect student wallet balances
```

### Why These Technologies Were Chosen

| Component | Technology | Why We Chose It (Student Perspective) |
|---|---|---|
| **Backend Framework** | **FastAPI (Python)** | Extremely fast, easy to write clean REST APIs, automatically generates interactive Swagger API documentation (`/docs`), and handles concurrent requests smoothly. |
| **Database** | **MySQL 8.0** | Reliable, widely taught in university database courses, supports ACID transactions (so money calculations never glitch), and has built-in foreign key constraints. |
| **Frontend** | **HTML5 + CSS3 + JavaScript** | Lightweight, requires zero build setup or heavy node modules, loads instantly on low-bandwidth campus Wi-Fi, and works on both Android and iPhone browsers. |

---

## 6. DATABASE DESIGN & KEY TABLES

The database stores all campus activity across four main tables. Foreign key relationships ensure that no orphan records or invalid references can exist.

```
       +--------------------+                +-----------------------+
       |      STUDENTS      |                |         TASKS         |
       +--------------------+                +-----------------------+
       | reg_no (PK)        |<-------+       | task_id (PK)          |
       | name               |        |       | requester_id (FK)-----+
       | email              |        +-------| runner_id (FK, Null)  |
       | balance            |                | title, pickup, drop   |
       | trust_rating       |                | bounty, status        |
       +--------------------+                | verification_pin      |
                 ^                           +-----------------------+
                 |                                    |         |
                 |                                    |         |
         +-------+-------+                            |         |
         |               |                            |         |
+-------------------+ +----------------------------+  |         |
|       BIDS        | |    ESCROW_TRANSACTIONS     |  |         |
+-------------------+ +----------------------------+  |         |
| bid_id (PK)       | | txn_id (PK)                |  |         |
| task_id (FK)------+ | task_id (FK)---------------+--+         |
| runner_id (FK)----+ | amount                     |            |
| offered_time_mins | | escrow_status (HELD/REL..) |            |
| bid_status        | +----------------------------+            |
+-------------------+                                           |
```

### Brief Description of Tables:

1. **`students` Table:**
   - Stores user identity, student email, available wallet balance, and overall reputation score.
   - Example record: `(21BCE1042, "Ananya Sharma", "ananya@vitstudent.ac.in", ₹450.00, 4.8)`.

2. **`tasks` Table:**
   - Stores every errand created on the platform, along with pickup/drop locations, bounty value, current status (`open`, `assigned`, `in_transit`, `completed`, `cancelled`), and the secret 4-digit verification PIN.

3. **`bids` Table:**
   - Records every runner who volunteers for an errand, their offered delivery timeframe, and whether their bid was `pending`, `accepted`, or `rejected`.

4. **`escrow_transactions` Table:**
   - The financial ledger that tracks locked funds. Records when bounty money was placed into `HELD` status, and when it transitioned to `RELEASED` (paid to runner) or `REFUNDED` (returned to requester).

---

## 7. SAFETY & FAIRNESS MECHANISMS

When building an app where real or virtual money changes hands among college students, safety is paramount. Campus Runner includes three key safeguards:

### 7.1 Prevention of Self-Bidding
Students should not be allowed to bid on their own errands to artificially manipulate ratings or test edge-cases. The system automatically verifies that:
$$\text{Requester ID} \neq \text{Runner ID}$$
If a user attempts to place a bid on a task they created, the system immediately rejects the request with a friendly error message: *"You cannot bid on your own errand."*

### 7.2 Zero Financial Loss (Escrow Invariant)
In simple apps, a common bug occurs if a student's phone battery dies or internet drops while paying. Campus Runner guarantees that **money is never created or destroyed**:
$$\text{Requester Wallet Balance} + \text{Runner Wallet Balance} + \text{Escrow Held Amount} = \text{Constant Total}$$
Either the errand completes successfully and the runner gets the bounty, or the errand is aborted and the requester receives their full refund.

### 7.3 Protection Against Double Claiming
If two runners click "Accept" or "Submit PIN" at the exact same millisecond, the database uses **row-level locking**. Only the first runner's request is accepted; the second runner is cleanly notified that the task has already been claimed, preventing duplicate payouts.

---

## 8. STEP-BY-STEP USER JOURNEY: A REAL-LIFE EXAMPLE

To visualize how the platform works in practice, consider the following everyday scenario at VIT:

```
+-------------------------------------------------------------------------------+
|                       CAMPUS RUNNER IN ACTION                                 |
+-------------------------------------------------------------------------------+
| 1. Ananya (Student Requester - Block D Hostel)                                |
|    * Has a lab submission in 45 minutes.                                      |
|    * Needs 15 pages printed from the Central Library Xerox Shop.              |
|    * Opens Campus Runner, clicks "Post Task":                                 |
|        - Title: "Urgent 15-Page Lab Report Printout"                          |
|        - Pickup: Central Library Ground Floor Xerox                           |
|        - Drop: Hostel Block D, Room 412                                       |
|        - Bounty: ₹50.00                                                       |
|    * System verifies Ananya has ₹200 wallet balance.                          |
|    * ₹50 is safely moved into ESCROW. Her balance is now ₹150.                |
|    * Task appears on the Live Errand Feed as 'OPEN'.                          |
+-------------------------------------------------------------------------------+
| 2. Rohan (Student Runner - Near Library)                                      |
|    * Just finished studying in the library and is walking back towards Block D|
|    * Opens Campus Runner, spots Ananya's errand offering ₹50.                 |
|    * Places a bid: "Can deliver in 15 minutes."                               |
+-------------------------------------------------------------------------------+
| 3. Assignment & PIN Generation                                                |
|    * Ananya sees Rohan's bid (4.9-star rating, 15 mins).                      |
|    * Ananya clicks "Assign Rohan".                                            |
|    * Ananya's screen now displays: "Secret Handover PIN: 8492".               |
|    * Rohan's phone updates to: "Head to Library Xerox, then deliver to D-412" |
+-------------------------------------------------------------------------------+
| 4. Physical Handover & Instant Payout                                         |
|    * Rohan collects the prints, walks to Block D, and meets Ananya.           |
|    * Rohan hands over the printed document.                                   |
|    * Ananya verifies the pages and tells Rohan: "PIN is 8492".                |
|    * Rohan types "8492" into his Campus Runner app and clicks "Verify".       |
|    * The app confirms the match!                                              |
|    * The ₹50 Escrow is unlocked and instantly credited to Rohan's wallet.     |
|    * Both students leave satisfied with zero awkward cash exchanges!          |
+-------------------------------------------------------------------------------+
```

---

## 9. TESTING & FUNCTIONAL VERIFICATION

The platform underwent thorough functional testing across multiple devices (Laptops, Android, iOS):

| Test Case | Scenario Tested | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| **TC-01** | Student posts task with insufficient wallet balance | Error: "Insufficient balance to fund bounty escrow" | Blocked with clear user alert | **PASS** |
| **TC-02** | Student attempts to bid on their own task | Error: "Self-bidding is not permitted" | Action rejected by system | **PASS** |
| **TC-03** | Requester assigns runner from multiple bids | Winning runner assigned; competing bids marked rejected | Assigned cleanly; others updated | **PASS** |
| **TC-04** | Runner submits incorrect 4-digit PIN at handover | Error: "Invalid verification token" | Task remains in transit; no money released | **PASS** |
| **TC-05** | Runner submits correct 4-digit PIN | Escrow released; Runner wallet credited; Status = completed | Completed instantly with success badge | **PASS** |
| **TC-06** | Requester cancels open task with no runner | Escrow refunded back to requester wallet | Balance restored by exact bounty amount | **PASS** |

---

## 10. CHALLENGES FACED & SOLUTIONS

1. **Challenge: Preventing Fraudulent Handover Claims**  
   *Initial thought:* Let runners click "Delivered" and requesters click "Received".  
   *Problem:* If the requester forgets to click "Received", the runner's money is stuck forever. If the runner clicks "Delivered" without delivering, the requester loses money.  
   *Solution:* We implemented the **single-use 4-Digit Handover PIN**. Because only the requester has the PIN, the runner cannot falsely claim completion without physical contact.

2. **Challenge: Handling Slow or Flaky Campus Wi-Fi**  
   *Problem:* Heavy web applications built with large frontend frameworks often fail to load properly on crowded campus hostel networks.  
   *Solution:* We kept the frontend lightweight using vanilla HTML5, clean CSS, and lightweight asynchronous JavaScript `fetch()` calls. The app loads in under 1 second.

3. **Challenge: Managing Wallet Integrity Without Real Banking APIs**  
   *Problem:* Implementing real bank gateways requires business registration and commercial approval not feasible for academic student projects.  
   *Solution:* We built an in-app simulated credit ledger that strictly mimics digital banking: balances cannot be negative, all transactions are recorded in an audit trail, and money is held in escrow during active jobs.

---

## 11. LIMITATIONS & FUTURE ENHANCEMENTS

While the current system is fully functional and stable, several exciting enhancements can be explored:
- **Direct UPI / Payment Gateway Integration:** Integrating gateways like Razorpay or PhonePe to allow students to add and withdraw real money directly to their bank accounts.
- **Campus Map & Route Tracking:** Adding an interactive campus map (e.g., using OpenStreetMap or Leaflet.js) to show walking distances between academic blocks and hostels.
- **Push Notifications & WhatsApp Alerts:** Sending automated WhatsApp or web-push notifications when a bid is accepted or when a runner arrives at the hostel gate.
- **Item Photo Proof:** Allowing requesters to upload a photo of the receipt or item to verify costs before handover.

---

## 12. CONCLUSION & KEY LEARNINGS

The **Campus Runner** project demonstrates how modern full-stack web engineering and sound database design principles can solve an everyday problem faced by thousands of residential college students. By combining a transparent bidding mechanism, an escrow-based wallet, and a simple 4-digit physical verification code, the platform establishes trust between students who have never met before.

### Key Learnings from the Project:
- Gained hands-on experience in building asynchronous web APIs using Python and **FastAPI**.
- Understood the importance of **database transactions** and **state machines** in financial and errand workflows.
- Developed an appreciation for **User-Centered Design**, focusing on simplicity, mobile responsiveness, and high readability for college students.
- Learned how to bridge software solutions with physical real-world interactions (such as physical parcel handovers).

---

## 13. REFERENCES

1. FastAPI Documentation: *High performance, easy to learn, fast to code.* https://fastapi.tiangolo.com/
2. MySQL 8.0 Reference Manual: *Transaction Model and Locking Mechanisms.* Oracle Corporation, 2024.
3. MDN Web Docs: *Responsive Web Design, Fetch API, and Modern DOM Manipulation.* Mozilla Developer Network.
4. J. Gray and A. Reuter, *Transaction Processing: Concepts and Techniques*. Morgan Kaufmann, 1992.
5. Campus Task Dispatcher Repository: https://github.com/rajveermodi/p2p-campus-task-dispatcher
