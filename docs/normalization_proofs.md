# Formal Relational Schema Normalization & BCNF Proofs

**Project:** High-Concurrency Peer-to-Peer Campus Task & Errand Dispatcher  
**Database Engine:** MySQL 8.0 InnoDB  
**Target Normal Form:** Boyce-Codd Normal Form (BCNF)  

---

## 1. Executive Summary

This document establishes the formal relational algebra and functional dependency proofs demonstrating that the relational schema of the Campus Errand Dispatcher is strictly normalized to **Boyce-Codd Normal Form (BCNF)**. 

Normalization to BCNF eliminates all redundancy-induced update, insertion, and deletion anomalies while ensuring that the schema decomposition achieves:
1. **Lossless-Join Decomposition Property** ($\Pi_{R_1}(R) \bowtie \Pi_{R_2}(R) \bowtie \dots \bowtie \Pi_{R_n}(R) = R$).
2. **Strict Functional Dependency Preservation** ($(\bigcup F_i)^+ = F^+$).

---

## 2. Universal Relation Schema & Global Functional Dependencies

Let the universal un-normalized errand marketplace schema be denoted as:
$$U = \{ \text{Reg\_No}, \text{Student\_Name}, \text{Email}, \text{Trust\_Rating}, \text{Balance}, \text{Student\_Created\_At}, \text{Task\_ID}, \text{Requester\_ID}, \text{Runner\_ID}, \text{Pickup\_Location}, \text{Drop\_Location}, \text{Bounty}, \text{Task\_Status}, \text{Verification\_Pin}, \text{Task\_Created\_At}, \text{Bid\_ID}, \text{Bid\_Runner\_ID}, \text{Offered\_Time}, \text{Bid\_Status}, \text{Bid\_Created\_At}, \text{Txn\_ID}, \text{Escrow\_Amount}, \text{Escrow\_State}, \text{Released\_At}, \text{Escrow\_Updated\_At} \}$$

The canonical set of functional dependencies $F$ governing the campus domain consists of:
1. $\text{Reg\_No} \to \{ \text{Student\_Name}, \text{Email}, \text{Trust\_Rating}, \text{Balance}, \text{Student\_Created\_At} \}$
2. $\text{Email} \to \{ \text{Reg\_No}, \text{Student\_Name}, \text{Trust\_Rating}, \text{Balance}, \text{Student\_Created\_At} \}$
3. $\text{Task\_ID} \to \{ \text{Requester\_ID}, \text{Runner\_ID}, \text{Pickup\_Location}, \text{Drop\_Location}, \text{Bounty}, \text{Task\_Status}, \text{Verification\_Pin}, \text{Task\_Created\_At} \}$
4. $\text{Bid\_ID} \to \{ \text{Task\_ID}, \text{Bid\_Runner\_ID}, \text{Offered\_Time}, \text{Bid\_Status}, \text{Bid\_Created\_At} \}$
5. $\{ \text{Task\_ID}, \text{Bid\_Runner\_ID} \} \to \{ \text{Bid\_ID}, \text{Offered\_Time}, \text{Bid\_Status}, \text{Bid\_Created\_At} \}$
6. $\text{Txn\_ID} \to \{ \text{Task\_ID}, \text{Escrow\_Amount}, \text{Escrow\_State}, \text{Released\_At}, \text{Escrow\_Updated\_At} \}$
7. $\text{Task\_ID} \to \{ \text{Txn\_ID}, \text{Escrow\_Amount}, \text{Escrow\_State}, \text{Released\_At}, \text{Escrow\_Updated\_At} \}$

To eliminate cross-domain redundancy, $U$ is decomposed into 4 distinct relations:
$$\mathcal{D} = \{ R_1 = \text{Students}, R_2 = \text{Tasks}, R_3 = \text{Bids}, R_4 = \text{Escrow\_Transactions} \}$$

---

## 3. Detailed Per-Relation Normalization Proofs

### 3.1. Relation 1: `Students`

#### Attribute Set
$$R_1(\underline{\text{Reg\_No}}, \text{Name}, \text{Email}, \text{Trust\_Rating}, \text{Balance}, \text{Created\_At})$$

#### Functional Dependency Set ($F_1$)
$$F_1 = \{ f_{1a}: \text{Reg\_No} \to \{ \text{Name}, \text{Email}, \text{Trust\_Rating}, \text{Balance}, \text{Created\_At} \}, \quad f_{1b}: \text{Email} \to \{ \text{Reg\_No}, \text{Name}, \text{Trust\_Rating}, \text{Balance}, \text{Created\_At} \} \}$$

#### Candidate Key Derivation (Attribute Closure)
1. Compute closure of $\{ \text{Reg\_No} \}$:
   $$\{ \text{Reg\_No} \}^+ = \{ \text{Reg\_No}, \text{Name}, \text{Email}, \text{Trust\_Rating}, \text{Balance}, \text{Created\_At} \} = R_1$$
   Since no proper subset of $\{ \text{Reg\_No} \}$ determines $R_1$, $K_1 = \{ \text{Reg\_No} \}$ is a minimal candidate key.
2. Compute closure of $\{ \text{Email} \}$:
   $$\{ \text{Email} \}^+ = \{ \text{Email}, \text{Reg\_No}, \text{Name}, \text{Trust\_Rating}, \text{Balance}, \text{Created\_At} \} = R_1$$
   Since no proper subset of $\{ \text{Email} \}$ determines $R_1$, $K_2 = \{ \text{Email} \}$ is an alternate minimal candidate key.

- **Set of Candidate Keys:** $\mathcal{K}_1 = \{ \{ \text{Reg\_No} \}, \{ \text{Email} \} \}$
- **Prime Attributes:** $\{ \text{Reg\_No}, \text{Email} \}$
- **Non-Prime Attributes:** $\{ \text{Name}, \text{Trust\_Rating}, \text{Balance}, \text{Created\_At} \}$

#### Normal Form Verification Steps
- **1NF:** Every column contains exclusively atomic, scalar values (domain constraint). There are no repeating groups or composite nested structures. $\implies \mathbf{1NF\ Satisfied}$.
- **2NF:** A relation is in 2NF if it is in 1NF and every non-prime attribute is fully functionally dependent on each candidate key. Since both candidate keys $K_1$ and $K_2$ are singleton sets (cardinality 1), no proper subset exists. Thus, partial dependencies cannot exist. $\implies \mathbf{2NF\ Satisfied}$.
- **3NF:** A relation is in 3NF if for every non-trivial FD $X \to Y \in F_1^+$, either $X$ is a superkey or $Y$ is a subset of a candidate key (prime attribute). For both $f_{1a}$ and $f_{1b}$, the left-hand sides ($\text{Reg\_No}$ and $\text{Email}$) are superkeys. No transitive dependency of the form $\text{Non-Prime} \to \text{Non-Prime}$ exists. $\implies \mathbf{3NF\ Satisfied}$.
- **Strict BCNF Proof:**  
  A relation is in BCNF if and only if for every non-trivial functional dependency $X \to Y \in F_1^+$, $X$ is a superkey of $R_1$.  
  - For $f_{1a}: \text{Reg\_No} \to R_1 \setminus \{ \text{Reg\_No} \}$, $\text{Reg\_No}$ is a candidate key $\implies$ Superkey.
  - For $f_{1b}: \text{Email} \to R_1 \setminus \{ \text{Email} \}$, $\text{Email}$ is a candidate key $\implies$ Superkey.
  
  $$\therefore \mathbf{Students\ is\ strictly\ in\ Boyce\text{-}Codd\ Normal\ Form\ (BCNF).}$$

---

### 3.2. Relation 2: `Tasks`

#### Attribute Set
$$R_2(\underline{\text{Task\_ID}}, \text{Requester\_ID}, \text{Runner\_ID}, \text{Pickup\_Location}, \text{Drop\_Location}, \text{Bounty}, \text{Status}, \text{Verification\_Pin}, \text{Created\_At})$$

#### Functional Dependency Set ($F_2$)
$$F_2 = \{ f_{2a}: \text{Task\_ID} \to \{ \text{Requester\_ID}, \text{Runner\_ID}, \text{Pickup\_Location}, \text{Drop\_Location}, \text{Bounty}, \text{Status}, \text{Verification\_Pin}, \text{Created\_At} \} \}$$

*(Note: $\text{Requester\_ID} \not\to \text{Task\_ID}$ and $\text{Runner\_ID} \not\to \text{Task\_ID}$ as one student may create or execute multiple tasks).*

#### Candidate Key Derivation
1. Compute closure of $\{ \text{Task\_ID} \}$:
   $$\{ \text{Task\_ID} \}^+ = R_2$$
- **Candidate Key:** $K = \{ \text{Task\_ID} \}$
- **Prime Attribute:** $\{ \text{Task\_ID} \}$
- **Non-Prime Attributes:** $\{ \text{Requester\_ID}, \text{Runner\_ID}, \text{Pickup\_Location}, \text{Drop\_Location}, \text{Bounty}, \text{Status}, \text{Verification\_Pin}, \text{Created\_At} \}$

#### Normal Form Verification Steps
- **1NF:** All attributes hold atomic values. Status is an atomic enumerated scalar $\in \{\text{'open'}, \text{'assigned'}, \text{'in\_transit'}, \text{'completed'}, \text{'cancelled'}\}$. Verification PIN is an atomic 4-digit token. $\implies \mathbf{1NF\ Satisfied}$.
- **2NF:** The candidate key is single-attribute ($\text{Task\_ID}$). No partial dependencies can exist. $\implies \mathbf{2NF\ Satisfied}$.
- **3NF:** No non-prime attribute determines any other non-prime attribute (locations, bounty, status, and pin are mutually independent given $\text{Task\_ID}$). $\implies \mathbf{3NF\ Satisfied}$.
- **Strict BCNF Proof:**  
  The only non-trivial functional dependencies in $F_2^+$ are of the form $\text{Task\_ID} \to Y$. Since $\text{Task\_ID}$ is a candidate key (and therefore a superkey), every determinant is a superkey.
  
  $$\therefore \mathbf{Tasks\ is\ strictly\ in\ Boyce\text{-}Codd\ Normal\ Form\ (BCNF).}$$

---

### 3.3. Relation 3: `Bids`

#### Attribute Set
$$R_3(\underline{\text{Bid\_ID}}, \text{Task\_ID}, \text{Runner\_ID}, \text{Offered\_Time}, \text{Bid\_Status}, \text{Created\_At})$$

#### Functional Dependency Set ($F_3$)
$$F_3 = \{ f_{3a}: \text{Bid\_ID} \to \{ \text{Task\_ID}, \text{Runner\_ID}, \text{Offered\_Time}, \text{Bid\_Status}, \text{Created\_At} \}, \quad f_{3b}: \{ \text{Task\_ID}, \text{Runner\_ID} \} \to \{ \text{Bid\_ID}, \text{Offered\_Time}, \text{Bid\_Status}, \text{Created\_At} \} \}$$

*(The dependency $f_{3b}$ is enforced by the candidate key constraint `uq_task_runner UNIQUE (Task_ID, Runner_ID)`, ensuring each runner submits at most one bid per task).*

#### Candidate Key Derivation
1. Compute closure of $\{ \text{Bid\_ID} \}$:
   $$\{ \text{Bid\_ID} \}^+ = R_3$$
2. Compute closure of $\{ \text{Task\_ID}, \text{Runner\_ID} \}$:
   $$\{ \text{Task\_ID}, \text{Runner\_ID} \}^+ = R_3$$
   No proper subset ($\{ \text{Task\_ID} \}$ or $\{ \text{Runner\_ID} \}$) determines the remaining attributes because multiple runners bid on one task, and one runner bids across multiple tasks.

- **Set of Candidate Keys:** $\mathcal{K}_3 = \{ \{ \text{Bid\_ID} \}, \{ \text{Task\_ID}, \text{Runner\_ID} \} \}$
- **Prime Attributes:** $\{ \text{Bid\_ID}, \text{Task\_ID}, \text{Runner\_ID} \}$
- **Non-Prime Attributes:** $\{ \text{Offered\_Time}, \text{Bid\_Status}, \text{Created\_At} \}$

#### Normal Form Verification Steps
- **1NF:** All attributes are scalar values. $\implies \mathbf{1NF\ Satisfied}$.
- **2NF:** For composite key $\{ \text{Task\_ID}, \text{Runner\_ID} \}$, does any proper subset determine a non-prime attribute?  
  - $\text{Task\_ID} \not\to \text{Bid\_Status}$  
  - $\text{Runner\_ID} \not\to \text{Bid\_Status}$  
  Hence, no partial dependency exists. $\implies \mathbf{2NF\ Satisfied}$.
- **3NF:** In both $f_{3a}$ and $f_{3b}$, the determinants ($\text{Bid\_ID}$ and $\{ \text{Task\_ID}, \text{Runner\_ID} \}$) are superkeys. $\implies \mathbf{3NF\ Satisfied}$.
- **Strict BCNF Proof:**  
  For all non-trivial functional dependencies $X \to Y \in F_3^+$:
  - If $X = \text{Bid\_ID}$, $X$ is a superkey.
  - If $X = \{ \text{Task\_ID}, \text{Runner\_ID} \}$, $X$ is a superkey.
  
  $$\therefore \mathbf{Bids\ is\ strictly\ in\ Boyce\text{-}Codd\ Normal\ Form\ (BCNF).}$$

---

### 3.4. Relation 4: `Escrow_Transactions`

#### Attribute Set
$$R_4(\underline{\text{Txn\_ID}}, \text{Task\_ID}, \text{Amount}, \text{Escrow\_State}, \text{Released\_At}, \text{Updated\_At})$$

#### Functional Dependency Set ($F_4$)
$$F_4 = \{ f_{4a}: \text{Txn\_ID} \to \{ \text{Task\_ID}, \text{Amount}, \text{Escrow\_State}, \text{Released\_At}, \text{Updated\_At} \}, \quad f_{4b}: \text{Task\_ID} \to \{ \text{Txn\_ID}, \text{Amount}, \text{Escrow\_State}, \text{Released\_At}, \text{Updated\_At} \} \}$$

*(Enforced by `uq_escrow_task UNIQUE (Task_ID)`, guaranteeing a strictly 1:1 escrow ledger allocation per task).*

#### Candidate Key Derivation
1. $\{ \text{Txn\_ID} \}^+ = R_4 \implies K_1 = \{ \text{Txn\_ID} \}$
2. $\{ \text{Task\_ID} \}^+ = R_4 \implies K_2 = \{ \text{Task\_ID} \}$

- **Set of Candidate Keys:** $\mathcal{K}_4 = \{ \{ \text{Txn\_ID} \}, \{ \text{Task\_ID} \} \}$
- **Prime Attributes:** $\{ \text{Txn\_ID}, \text{Task\_ID} \}$
- **Non-Prime Attributes:** $\{ \text{Amount}, \text{Escrow\_State}, \text{Released\_At}, \text{Updated\_At} \}$

#### Normal Form Verification Steps
- **1NF:** All attributes atomic. $\implies \mathbf{1NF\ Satisfied}$.
- **2NF:** All candidate keys are singleton sets; no partial dependencies possible. $\implies \mathbf{2NF\ Satisfied}$.
- **3NF:** Determinants are superkeys. $\implies \mathbf{3NF\ Satisfied}$.
- **Strict BCNF Proof:**  
  Every determinant in $F_4^+$ ($\text{Txn\_ID}$ and $\text{Task\_ID}$) is a minimal candidate key and therefore a superkey of $R_4$.
  
  $$\therefore \mathbf{Escrow\_Transactions\ is\ strictly\ in\ Boyce\text{-}Codd\ Normal\ Form\ (BCNF).}$$

---

## 4. Lossless-Join Decomposition Verification

A decomposition $\mathcal{D} = \{ R_1, R_2, \dots, R_k \}$ of schema $R$ is **lossless** with respect to functional dependency set $F$ if:
$$\Pi_{R_1}(R) \bowtie \Pi_{R_2}(R) \bowtie \dots \bowtie \Pi_{R_k}(R) = R$$

### Stepwise Verification via Binary Natural Joins (Heath's Theorem)
Heath's Theorem states that a binary decomposition $\{ R_A, R_B \}$ of $R$ is lossless if and only if:
$$(R_A \cap R_B) \to R_A \quad \text{or} \quad (R_A \cap R_B) \to R_B$$

1. **Join Step 1:** $R_1 (\text{Students}) \bowtie R_2 (\text{Tasks})$
   $$R_1 \cap R_2 = \{ \text{Reg\_No} \}$$
   *(Note: $\text{Tasks.Requester\_ID}$ references $\text{Students.Reg\_No}$).*  
   Since $\text{Reg\_No} \to R_1$ in $F_1$, $R_1 \cap R_2$ is a superkey of $R_1$.  
   $$\therefore R_1 \bowtie R_2 \text{ is a lossless join.}$$

2. **Join Step 2:** $(R_1 \bowtie R_2) \bowtie R_4 (\text{Escrow\_Transactions})$
   $$(R_1 \cup R_2) \cap R_4 = \{ \text{Task\_ID} \}$$
   Since $\text{Task\_ID} \to R_4$ in $F_4$ (via candidate key $K_2$), $(R_1 \cup R_2) \cap R_4$ is a superkey of $R_4$.  
   $$\therefore (R_1 \bowtie R_2) \bowtie R_4 \text{ is a lossless join.}$$

3. **Join Step 3:** $(R_1 \bowtie R_2 \bowtie R_4) \bowtie R_3 (\text{Bids})$
   $$(R_1 \cup R_2 \cup R_4) \cap R_3 = \{ \text{Task\_ID}, \text{Runner\_ID} \}$$
   Since $\{ \text{Task\_ID}, \text{Runner\_ID} \} \to R_3$ in $F_3$, the intersection is a superkey of $R_3$.  
   $$\therefore \text{The entire decomposition } \mathcal{D} = \{ \text{Students}, \text{Tasks}, \text{Bids}, \text{Escrow\_Transactions} \} \text{ is strictly lossless.}$$

---

## 5. Functional Dependency Preservation Verification

A decomposition $\mathcal{D} = \{ R_1, R_2, R_3, R_4 \}$ preserves a dependency set $F$ if:
$$(\bigcup_{i=1}^4 \pi_{R_i}(F))^+ = F^+$$

Let us check each dependency in $F$:
1. $\text{Reg\_No} \to \text{Students attributes} \in \pi_{R_1}(F)$ $\implies \mathbf{Preserved\ in\ } R_1$.
2. $\text{Email} \to \text{Students attributes} \in \pi_{R_1}(F)$ $\implies \mathbf{Preserved\ in\ } R_1$.
3. $\text{Task\_ID} \to \text{Tasks attributes} \in \pi_{R_2}(F)$ $\implies \mathbf{Preserved\ in\ } R_2$.
4. $\text{Bid\_ID} \to \text{Bids attributes} \in \pi_{R_3}(F)$ $\implies \mathbf{Preserved\ in\ } R_3$.
5. $\{ \text{Task\_ID}, \text{Bid\_Runner\_ID} \} \to \text{Bids attributes} \in \pi_{R_3}(F)$ $\implies \mathbf{Preserved\ in\ } R_3$.
6. $\text{Txn\_ID} \to \text{Escrow attributes} \in \pi_{R_4}(F)$ $\implies \mathbf{Preserved\ in\ } R_4$.
7. $\text{Task\_ID} \to \text{Escrow attributes} \in \pi_{R_4}(F)$ $\implies \mathbf{Preserved\ in\ } R_4$.

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
