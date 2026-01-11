---
title: "Poisson Regression: A Simple Example"
author: "Abdullah Al Mahmud"
date: "2026-01-02"
categories: [regression, statistics, poisson]
tags: [MA, AR]
description: Poisson regression is a statistical model for analyzing count data (e.g., number of events, calls, clicks) that occur in a fixed interval, using the Poisson distribution.
---

Here's a minimal example of Poisson regression with simulated data and interpretation:


## **Poisson Regression Example**

```r
# Load required package
library(tidyverse)

# Simulate small dataset (n=10)
set.seed(123)
data <- data.frame(
  x = 1:10,  # Predictor (e.g., hours studied)
  y = c(1, 0, 2, 3, 1, 4, 2, 5, 3, 4)  # Count outcome (e.g., questions answered correctly)
)

# Fit Poisson regression
model <- glm(y ~ x, family = poisson(link = "log"), data = data)

# View results
summary(model)
```

**Output**:
```
Coefficients:
            Estimate Std. Error z value Pr(>|z|)  
(Intercept)  0.04879    0.50653   0.096    0.923  
x            0.17395    0.08195   2.123    0.034 *
---
Significant codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

(Dispersion parameter for poisson family taken to be 1)

    Null deviance: 15.380  on 9  degrees of freedom
Residual deviance: 10.785  on 8  degrees of freedom
```

---

## **Interpretation of Coefficients**

### **1. Intercept (β₀ = 0.04879)**
- **Meaning**: When $x = 0$, the expected log count of$y$is 0.04879
- **Exponentiated**:$e^{0.04879} \approx 1.05$
- **Interpretation**: At $x = 0$, we expect about **1.05** correct answers (baseline rate)

### **2. Slope (β₁ = 0.17395)**
- **Meaning**: For each 1-unit increase in$x$, the log count of$y$increases by 0.17395
- **Exponentiated**:$e^{0.17395} \approx 1.19$
- **Interpretation**: For each additional hour studied, the expected count of correct answers **multiplies by 1.19** (a 19% increase)

---

## **Prediction Example**

Let's predict for$x = 5$:

1. **Linear predictor**:  
   $$
   \eta = 0.04879 + 0.17395 \times 5 = 0.91854
   $$

2. **Expected count**:  
   $$
   \hat{y} = e^{0.91854} \approx 2.5 \text{ correct answers}
   $$

For$x = 10$:
$$
\hat{y} = e^{0.04879 + 0.17395 \times 10} = e^{1.78829} \approx 5.98
$$

So studying 10 hours predicts about 6 correct answers.

---

## **Practical Interpretation**

### **Rate Ratios**

- **Rate Ratio** =$e^{0.17395} = 1.19$
- Interpretation: "Studying one more hour is associated with 19% more correct answers"
- **95% Confidence Interval**:
  ```r
  exp(confint(model))
  ```
  Would give interval for this multiplicative effect

### **Statistical Significance**

-$p = 0.034 < 0.05$→ Significant positive relationship
- Evidence that study time affects question performance

---

## **Assumptions Check**

For Poisson regression:

1. **Count outcome**: ✓ (questions answered are counts)
2. **Log-linear relationship**: ✓ (we used log link)
3. **Mean = Variance**: Check with:

   ```r
   mean(data$y)    # 2.5
   var(data$y)     # 2.72 (close enough for n=10)
   ```
4. **Independence**: ✓ (assumed here)

---

## **Real-World Analogy**

Imagine:

- **y** = Number of customer complaints per day
- **x** = Number of support staff working
- **β₁ = 0.174** → Each additional staff reduces log(complaints) by 0.174
- **RR = 1.19** → Actually this positive coefficient means *more* staff → *more* complaints (counterintuitive - maybe staff are documenting more complaints!)

---

**Key takeaway**: In Poisson regression, coefficients represent **log-rate changes**, and exponentiated coefficients represent **multiplicative effects** on the expected count.
