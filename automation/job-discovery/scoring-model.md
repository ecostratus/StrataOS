# Job Scoring Model

## Purpose

Provide objective scoring mechanism for prioritizing job opportunities based on defined criteria.

## Scoring Dimensions

### Role Fit (0-10 points)
- Title match to target roles
- Seniority level alignment
- Required skills match
- Domain expertise match

**Weighting**: 35%

### Company Fit (0-10 points)
- Company size preference
- Industry alignment
- Company culture indicators
- Growth stage
- Reputation/stability

**Weighting**: 20%

### Compensation & Benefits (0-10 points)
- Salary range (if posted)
- Benefits indicators
- Equity/bonus potential
- Work-life balance signals

**Weighting**: 20%

### Location & Flexibility (0-10 points)
- Remote/hybrid/onsite match
- Geographic preference
- Travel requirements
- Timezone compatibility

**Weighting**: 15%

### Growth Opportunity (0-10 points)
- Career advancement potential
- Learning opportunities
- Impact scope
- Team/leadership structure

**Weighting**: 10%

## Total Score Calculation

```
Total Score = (Role Fit × 0.35) + 
              (Company Fit × 0.20) + 
              (Compensation × 0.20) + 
              (Location × 0.15) + 
              (Growth × 0.10)
```

**Range**: 0-10 (weighted average)

## Score Interpretation

- **9-10**: Exceptional match - Priority action
- **7-8.9**: Strong match - Apply with tailored resume
- **5-6.9**: Moderate match - Consider if capacity allows
- **3-4.9**: Weak match - Low priority
- **0-2.9**: Poor match - Skip

## Scoring Method

### Automated Scoring
- Keyword matching for role fit
- Company data from external sources
- Location/flexibility from posting
- Salary data if available

### Manual Adjustment
- Override automated scores if needed
- Add subjective factors
- Document override rationale
- Track override patterns

## Configuration

### Customization Options
- Adjust dimension weightings
- Modify score thresholds
- Add custom scoring dimensions
- Define keyword lists for matching

### Scoring Updates
- Review scoring effectiveness monthly
- Adjust based on outcome data
- A/B test different scoring models
- Document scoring model changes

## Output

### Scored Job Records
- All scoring dimensions with values
- Total weighted score
- Score timestamp
- Scoring model version
- Manual override flag (if applicable)

## Validation

- Track correlation between score and outcomes
- Review high-scored rejections
- Review low-scored successes
- Adjust model based on validation data
