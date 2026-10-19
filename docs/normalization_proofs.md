# Formal Relational Schema Normalization & BCNF Proofs

**Project:** High-Concurrency Peer-to-Peer Campus Task & Errand Dispatcher  
**Database Engine:** MySQL 8.0 InnoDB  
**Target Normal Form:** Boyce-Codd Normal Form (BCNF)  

---

## 1. Executive Summary

This document establishes the formal relational algebra and functional dependency proofs demonstrating that the relational schema of the Campus Errand Dispatcher is strictly normalized to **Boyce-Codd Normal Form (BCNF)**. 

Normalization to BCNF eliminates all redundancy-induced update, insertion, and deletion anomalies while ensuring that the schema decomposition achieves:
1. **Lossless-Join Decomposition Property:**  
   $$\Pi_{R_1}(R) \bowtie \Pi_{R_2}(R) \bowtie \dots \bowtie \Pi_{R_n}(R) = R$$
2. **Strict Functional Dependency Preservation:**  
   $$(\bigcup_{i=1}^n \pi_{R_i}(F))^+ = F^+$$

---

## 2. Universal Relation Schema & Global Functional Dependencies

Let the universal un-normalized errand marketplace schema be denoted as:

> **Universal Schema ($U$):**  
> `U` = { `Reg_No`, `Student_Name`, `Email`, `Trust_Rating`, `Balance`, `Student_Created_At`, `Task_ID`, `Requester_ID`, `Runner_ID`, `Pickup_Location`, `Drop_Location`, `Bounty`, `Task_Status`, `Verification_Pin`, `Task_Created_At`, `Bid_ID`, `Bid_Runner_ID`, `Offered_Time`, `Bid_Status`, `Bid_Created_At`, `Txn_ID`, `Escrow_Amount`, `Escrow_State`, `Released_At`, `Escrow_Updated_At` }

The canonical set of functional dependencies $F$ governing the campus domain consists of:

1. `Reg_No` $\to$ { `Student_Name`, `Email`, `Trust_Rating`, `Balance`, `Student_Created_At` }
2. `Email` $\to$ { `Reg_No`, `Student_Name`, `Trust_Rating`, `Balance`, `Student_Created_At` }
3. `Task_ID` $\to$ { `Requester_ID`, `Runner_ID`, `Pickup_Location`, `Drop_Location`, `Bounty`, `Task_Status`, `Verification_Pin`, `Task_Created_At` }
4. `Bid_ID` $\to$ { `Task_ID`, `Bid_Runner_ID`, `Offered_Time`, `Bid_Status`, `Bid_Created_At` }
5. { `Task_ID`, `Bid_Runner_ID` } $\to$ { `Bid_ID`, `Offered_Time`, `Bid_Status`, `Bid_Created_At` }
6. `Txn_ID` $\to$ { `Task_ID`, `Escrow_Amount`, `Escrow_State`, `Released_At`, `Escrow_Updated_At` }
7. `Task_ID` $\to$ { `Txn_ID`, `Escrow_Amount`, `Escrow_State`, `Released_At`, `Escrow_Updated_At` }

To eliminate cross-domain redundancy, $U$ is decomposed into 4 distinct relations:
$$\mathcal{D} = \{ R_1 = \text{Students}, R_2 = \text{Tasks}, R_3 = \text{Bids}, R_4 = \text{EscrowTransactions} \}$$

---

## 3. Detailed Per-Relation Normalization Proofs

### 3.1. Relation 1: `Students`

#### Attribute Schema
`Students`(**`Reg_No`**, `Name`, `Email`, `Trust_Rating`, `Balance`, `Created_At`)  
*(Primary Key: `Reg_No`; Candidate Key: `Email`)*

#### Functional Dependency Set ($F_1$)
* $f_{1a}$: `Reg_No` $\to$ { `Name`, `Email`, `Trust_Rating`, `Balance`, `Created_At` }
* $f_{1b}$: `Email` $\to$ { `Reg_No`, `Name`, `Trust_Rating`, `Balance`, `Created_At` }

#### Candidate Key Derivation (Attribute Closure)
1. **Closure of `{ Reg_No }`:**  
   `{ Reg_No }`$^+$ = `{ Reg_No, Name, Email, Trust_Rating, Balance, Created_At }` = $R_1$  
   Since no proper subset of `{ Reg_No }` determines $R_1$, $K_1 =$ `{ Reg_No }` is a minimal candidate key.
2. **Closure of `{ Email }`:**  
   `{ Email }`$^+$ = `{ Email, Reg_No, Name, Trust_Rating, Balance, Created_At }` = $R_1$  
   Since no proper subset of `{ Email }` determines $R_1$, $K_2 =$ `{ Email }` is an alternate minimal candidate key.

* **Set of Candidate Keys:** $\mathcal{K}_1 =$ { `{ Reg_No }`, `{ Email }` }
* **Prime Attributes:** { `Reg_No`, `Email` }
* **Non-Prime Attributes:** { `Name`, `Trust_Rating`, `Balance`, `Created_At` }

#### Normal Form Verification Steps
* **1NF:** Every column contains exclusively atomic, scalar values (domain constraint). There are no repeating groups or composite nested structures. $\implies$ **1NF Satisfied**.
* **2NF:** A relation is in 2NF if it is in 1NF and every non-prime attribute is fully functionally dependent on each candidate key. Since both candidate keys $K_1$ and $K_2$ are singleton sets (cardinality 1), no proper subset exists. Thus, partial dependencies cannot exist. $\implies$ **2NF Satisfied**.
* **3NF:** A relation is in 3NF if for every non-trivial FD $X \to Y \in F_1^+$, either $X$ is a superkey or $Y$ is a subset of a candidate key (prime attribute). For both $f_{1a}$ and $f_{1b}$, the left-hand sides (`Reg_No` and `Email`) are superkeys. No transitive dependency of the form $\text{Non-Prime} \to \text{Non-Prime}$ exists. $\implies$ **3NF Satisfied**.
* **Strict BCNF Proof:**  
  A relation is in BCNF if and only if for every non-trivial functional dependency $X \to Y \in F_1^+$, $X$ is a superkey of $R_1$.  
  * For $f_{1a}$: `Reg_No` $\to R_1 \setminus$ `{ Reg_No }`, `Reg_No` is a candidate key $\implies$ Superkey.
  * For $f_{1b}$: `Email` $\to R_1 \setminus$ `{ Email }`, `Email` is a candidate key $\implies$ Superkey.
  
  $$\therefore \mathbf{Students\ is\ strictly\ in\ Boyce\text{-}Codd\ Normal\ Form\ (BCNF).}$$

---

### 3.2. Relation 2: `Tasks`

#### Attribute Schema
`Tasks`(**`Task_ID`**, `Requester_ID`, `Runner_ID`, `Pickup_Location`, `Drop_Location`, `Bounty`, `Status`, `Verification_Pin`, `Created_At`)  
*(Primary Key: `Task_ID`)*

#### Functional Dependency Set ($F_2$)
* $f_{2a}$: `Task_ID` $\to$ { `Requester_ID`, `Runner_ID`, `Pickup_Location`, `Drop_Location`, `Bounty`, `Status`, `Verification_Pin`, `Created_At` }

*(Note: `Requester_ID` $\not\to$ `Task_ID` and `Runner_ID` $\not\to$ `Task_ID` because a student may request or execute multiple tasks).*

#### Candidate Key Derivation
1. **Closure of `{ Task_ID }`:**  
   `{ Task_ID }`$^+$ = $R_2$

* **Candidate Key:** $K =$ `{ Task_ID }`
* **Prime Attribute:** { `Task_ID` }
* **Non-Prime Attributes:** { `Requester_ID`, `Runner_ID`, `Pickup_Location`, `Drop_Location`, `Bounty`, `Status`, `Verification_Pin`, `Created_At` }

#### Normal Form Verification Steps
* **1NF:** All attributes hold atomic values. `Status` is an atomic enumerated scalar $\in \{\text{'open'}, \text{'assigned'}, \text{'in-transit'}, \text{'completed'}, \text{'cancelled'}\}$. `Verification_Pin` is an atomic 4-digit token. $\implies$ **1NF Satisfied**.
* **2NF:** The candidate key is single-attribute (`Task_ID`). No partial dependencies can exist. $\implies$ **2NF Satisfied**.
* **3NF:** No non-prime attribute determines any other non-prime attribute (locations, bounty, status, and PIN are mutually independent given `Task_ID`). $\implies$ **3NF Satisfied**.
* **Strict BCNF Proof:**  
  The only non-trivial functional dependencies in $F_2^+$ are of the form `Task_ID` $\to Y$. Since `Task_ID` is a candidate key (and therefore a superkey), every determinant is a superkey.
  
  $$\therefore \mathbf{Tasks\ is\ strictly\ in\ Boyce\text{-}Codd\ Normal\ Form\ (BCNF).}$$

---

### 3.3. Relation 3: `Bids`

#### Attribute Schema
`Bids`(**`Bid_ID`**, `Task_ID`, `Runner_ID`, `Offered_Time`, `Bid_Status`, `Created_At`)  
*(Primary Key: `Bid_ID`; Alternate Candidate Key: `{ Task_ID, Runner_ID }`)*

#### Functional Dependency Set ($F_3$)
* $f_{3a}$: `Bid_ID` $\to$ { `Task_ID`, `Runner_ID`, `Offered_Time`, `Bid_Status`, `Created_At` }
* $f_{3b}$: { `Task_ID`, `Runner_ID` } $\to$ { `Bid_ID`, `Offered_Time`, `Bid_Status`, `Created_At` }

*(Dependency $f_{3b}$ is enforced by the unique candidate constraint `uq_task_runner UNIQUE (Task_ID, Runner_ID)`, preventing duplicate bids per errand).*

#### Candidate Key Derivation
1. **Closure of `{ Bid_ID }`:**  
   `{ Bid_ID }`$^+$ = $R_3$
2. **Closure of `{ Task_ID, Runner_ID }`:**  
   `{ Task_ID, Runner_ID }`$^+$ = $R_3$  
   No proper subset (`{ Task_ID }` or `{ Runner_ID }`) determines the remaining attributes because multiple runners bid on one task, and one runner bids across multiple tasks.

* **Set of Candidate Keys:** $\mathcal{K}_3 =$ { `{ Bid_ID }`, `{ Task_ID, Runner_ID }` }
* **Prime Attributes:** { `Bid_ID`, `Task_ID`, `Runner_ID` }
* **Non-Prime Attributes:** { `Offered_Time`, `Bid_Status`, `Created_At` }

#### Normal Form Verification Steps
* **1NF:** All attributes are scalar atomic values. $\implies$ **1NF Satisfied**.
* **2NF:** For composite key `{ Task_ID, Runner_ID }`, does any proper subset determine a non-prime attribute?  
  * `Task_ID` $\not\to$ `Bid_Status`  
  * `Runner_ID` $\not\to$ `Bid_Status`  
  Hence, no partial dependency exists. $\implies$ **2NF Satisfied**.
* **3NF:** In both $f_{3a}$ and $f_{3b}$, the determinants (`Bid_ID` and `{ Task_ID, Runner_ID }`) are superkeys. $\implies$ **3NF Satisfied**.
* **Strict BCNF Proof:**  
  For all non-trivial functional dependencies $X \to Y \in F_3^+$:
  * If $X =$ `Bid_ID`, $X$ is a superkey.
  * If $X =$ `{ Task_ID, Runner_ID }`, $X$ is a superkey.
  
  $$\therefore \mathbf{Bids\ is\ strictly\ in\ Boyce\text{-}Codd\ Normal\ Form\ (BCNF).}$$

---

### 3.4. Relation 4: `Escrow_Transactions`

#### Attribute Schema
`Escrow_Transactions`(**`Txn_ID`**, `Task_ID`, `Amount`, `Escrow_State`, `Released_At`, `Updated_At`)  
*(Primary Key: `Txn_ID`; Alternate Candidate Key: `Task_ID`)*

#### Functional Dependency Set ($F_4$)
* $f_{4a}$: `Txn_ID` $\to$ { `Task_ID`, `Amount`, `Escrow_State`, `Released_At`, `Updated_At` }
* $f_{4b}$: `Task_ID` $\to$ { `Txn_ID`, `Amount`, `Escrow_State`, `Released_At`, `Updated_At` }

*(Enforced by `uq_escrow_task UNIQUE (Task_ID)`, guaranteeing a strictly 1:1 escrow ledger allocation per task).*

#### Candidate Key Derivation
1. `{ Txn_ID }`$^+$ = $R_4 \implies K_1 =$ `{ Txn_ID }`
2. `{ Task_ID }`$^+$ = $R_4 \implies K_2 =$ `{ Task_ID }`

* **Set of Candidate Keys:** $\mathcal{K}_4 =$ { `{ Txn_ID }`, `{ Task_ID }` }
* **Prime Attributes:** { `Txn_ID`, `Task_ID` }
* **Non-Prime Attributes:** { `Amount`, `Escrow_State`, `Released_At`, `Updated_At` }

#### Normal Form Verification Steps
* **1NF:** All attributes atomic. $\implies$ **1NF Satisfied**.
* **2NF:** All candidate keys are singleton sets; no partial dependencies possible. $\implies$ **2NF Satisfied**.
* **3NF:** Determinants are superkeys. $\implies$ **3NF Satisfied**.
* **Strict BCNF Proof:**  
  Every determinant in $F_4^+$ (`Txn_ID` and `Task_ID`) is a minimal candidate key and therefore a superkey of $R_4$.
  
  $$\therefore \mathbf{Escrow\ Transactions\ is\ strictly\ in\ Boyce\text{-}Codd\ Normal\ Form\ (BCNF).}$$

---

## 4. Lossless-Join Decomposition Verification

A decomposition $\mathcal{D} = \{ R_1, R_2, \dots, R_k \}$ of schema $R$ is **lossless** with respect to functional dependency set $F$ if:
$$\Pi_{R_1}(R) \bowtie \Pi_{R_2}(R) \bowtie \dots \bowtie \Pi_{R_k}(R) = R$$

### Stepwise Verification via Binary Natural Joins (Heath's Theorem)
Heath's Theorem states that a binary decomposition $\{ R_A, R_B \}$ of $R$ is lossless if and only if:
$$(R_A \cap R_B) \to R_A \quad \text{or} \quad (R_A \cap R_B) \to R_B$$

1. **Join Step 1:** $R_1 (\text{Students}) \bowtie R_2 (\text{Tasks})$  
   $R_1 \cap R_2 =$ `{ Reg_No }`  
   *(Note: `Tasks.Requester_ID` references `Students.Reg_No`).*  
   Since `Reg_No` $\to R_1$ in $F_1$, $R_1 \cap R_2$ is a superkey of $R_1$.  
   $$\therefore R_1 \bowtie R_2 \text{ is a lossless join.}$$

2. **Join Step 2:** $(R_1 \bowtie R_2) \bowtie R_4 (\text{Escrow Transactions})$  
   $(R_1 \cup R_2) \cap R_4 =$ `{ Task_ID }`  
   Since `Task_ID` $\to R_4$ in $F_4$ (via candidate key $K_2$), $(R_1 \cup R_2) \cap R_4$ is a superkey of $R_4$.  
   $$\therefore (R_1 \bowtie R_2) \bowtie R_4 \text{ is a lossless join.}$$

3. **Join Step 3:** $(R_1 \bowtie R_2 \bowtie R_4) \bowtie R_3 (\text{Bids})$  
   $(R_1 \cup R_2 \cup R_4) \cap R_3 =$ `{ Task_ID, Runner_ID }`  
   Since `{ Task_ID, Runner_ID }` $\to R_3$ in $F_3$, the intersection is a superkey of $R_3$.  
   $$\therefore \text{The entire decomposition } \mathcal{D} = \{ \text{Students}, \text{Tasks}, \text{Bids}, \text{Escrow Transactions} \} \text{ is strictly lossless.}$$

---

## 5. Functional Dependency Preservation Verification

A decomposition $\mathcal{D} = \{ R_1, R_2, R_3, R_4 \}$ preserves a dependency set $F$ if:
$$(\bigcup_{i=1}^4 \pi_{R_i}(F))^+ = F^+$$

Let us check each dependency in $F$:
1. `Reg_No` $\to$ `Students` attributes $\in \pi_{R_1}(F) \implies$ **Preserved in $R_1$**.
2. `Email` $\to$ `Students` attributes $\in \pi_{R_1}(F) \implies$ **Preserved in $R_1$**.
3. `Task_ID` $\to$ `Tasks` attributes $\in \pi_{R_2}(F) \implies$ **Preserved in $R_2$**.
4. `Bid_ID` $\to$ `Bids` attributes $\in \pi_{R_3}(F) \implies$ **Preserved in $R_3$**.
5. { `Task_ID`, `Bid_Runner_ID` } $\to$ `Bids` attributes $\in \pi_{R_3}(F) \implies$ **Preserved in $R_3$**.
6. `Txn_ID` $\to$ `Escrow` attributes $\in \pi_{R_4}(F) \implies$ **Preserved in $R_4$**.
7. `Task_ID` $\to$ `Escrow` attributes $\in \pi_{R_4}(F) \implies$ **Preserved in $R_4$**.

No dependency requires a cross-relation multi-table join to evaluate.  
$$\therefore \mathbf{All\ Functional\ Dependencies\ are\ 100\%\ Preserved.}$$

---

## 6. Summary Matrix

| Relation | Primary Key | Alternate Candidate Keys | Prime Attributes | Normal Form | Lossless Join? | Dependency Preserved? |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **`Students`** | `Reg_No` | `Email` | `Reg_No`, `Email` | **BCNF** | Yes | Yes |
| **`Tasks`** | `Task_ID` | — | `Task_ID` | **BCNF** | Yes | Yes |
| **`Bids`** | `Bid_ID` | `(Task_ID, Runner_ID)` | `Bid_ID`, `Task_ID`, `Runner_ID` | **BCNF** | Yes | Yes |
| **`Escrow_Transactions`** | `Txn_ID` | `Task_ID` | `Txn_ID`, `Task_ID` | **BCNF** | Yes | Yes |
