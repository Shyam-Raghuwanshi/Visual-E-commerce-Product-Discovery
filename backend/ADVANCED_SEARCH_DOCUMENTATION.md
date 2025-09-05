# Advanced Search Logic Implementation Guide

## Overview

This document describes the implementation of sophisticated search algorithms that combine multiple similarity metrics, business logic, personalization, and A/B testing capabilities for the Visual E-commerce Product Discovery system.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Similarity Metrics](#similarity-metrics)
3. [Business Logic Engine](#business-logic-engine)
4. [Personalization Engine](#personalization-engine)
5. [Geographic Relevance](#geographic-relevance)
6. [A/B Testing Framework](#ab-testing-framework)
7. [Integration Guide](#integration-guide)
8. [Performance Optimization](#performance-optimization)
9. [Testing and Validation](#testing-and-validation)

## Architecture Overview

The advanced search system consists of several interconnected components:

```
┌─────────────────────────────────────────────────────────┐
│                Advanced Search Engine                   │
├─────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Similarity  │  │  Business Logic │  │Personalization│ │
│  │  Calculator   │  │     Engine      │  │    Engine   │ │
│  └───────────────┘  └─────────────────┘  └─────────────┘ │
│  ┌───────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │  Geographic   │  │   A/B Testing   │  │ Integration │ │
│  │   Context     │  │   Framework     │  │   Service   │ │
│  └───────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Similarity Metrics

### 1. Visual Similarity

Uses CLIP embeddings to calculate visual similarity between query images and product images.

```python
def calculate_visual_similarity(query_embedding, product_embedding):
    # Cosine similarity with non-linear transformation
    cosine_sim = dot_product(query_embedding, product_embedding) / (norm(query) * norm(product))
    enhanced_sim = 1 / (1 + exp(-10 * (cosine_sim - 0.5)))
    return enhanced_sim
```

**Features:**
- Cosine similarity calculation
- Non-linear transformation to spread scores
- Robust error handling
- Supports 512-dimensional CLIP embeddings

### 2. Textual Similarity

Combines multiple text matching techniques for comprehensive textual similarity.

**Components:**
- **Jaccard Similarity**: Token overlap between query and product text
- **Title Boost**: 30% boost for exact matches in product title
- **Brand Boost**: 20% boost for brand name matches
- **Category Boost**: 10% boost for category matches

```python
def calculate_textual_similarity(query_text, product_text, metadata):
    jaccard_sim = jaccard_similarity(query_tokens, product_tokens)
    title_boost = 0.3 if query in product_title else 0
    brand_boost = 0.2 if any_brand_match else 0
    category_boost = 0.1 if any_category_match else 0
    return min(1.0, jaccard_sim + title_boost + brand_boost + category_boost)
```

### 3. Categorical Similarity

Evaluates similarity based on product categories, subcategories, and tags.

**Scoring:**
- Direct category match: +0.4
- Sub-category match: +0.3
- Tag matches: +0.1 per match (max 0.3)

### 4. Behavioral Similarity

Analyzes user behavior patterns to determine product relevance.

**Factors:**
- Purchase history by category
- Brand loyalty scores
- Price range preferences
- Interaction patterns

## Business Logic Engine

### 1. Popularity Boost

Combines multiple popularity signals to boost well-performing products.

**Metrics Weighted:**
- Popularity Score (30%)
- View Count (20%) - normalized to 10k views max
- Purchase Count (30%) - normalized to 1k purchases max
- Rating (15%) - converted from 1-5 to 0-1 scale
- Review Count (5%) - normalized to 500 reviews max

### 2. Stock Availability

Applies stock-based scoring to prioritize available products.

**Scoring:**
- Out of stock: 0.1 (heavy penalty)
- Stock > 50: 1.0 (full score)
- Stock 10-50: 0.8
- Stock 1-9: 0.6
- Stock 0: 0.2

### 3. Price Competitiveness

Evaluates pricing competitiveness and discount attractiveness.

**Factors:**
- Discount percentage from original price
- Price vs. category average
- Combined scoring with discount boost

### 4. Conversion Rate Optimization

Boosts products with proven conversion performance.

**Metrics:**
- Conversion Rate (50% weight) - normalized to 20% max
- Add-to-Cart Rate (30% weight) - normalized to 30% max
- Return Rate Penalty (20% weight) - 10% return rate baseline

### 5. Geographic Relevance

Optimizes results based on user location and shipping factors.

**Components:**
- Regional availability (+0.3)
- Shipping cost optimization (+0.1)
- Shipping speed optimization (+0.1)
- Local popularity trends (+0.1)

## Personalization Engine

### 1. Preference Alignment

Matches products to user preferences across multiple dimensions.

**Alignment Factors:**
- Category Preferences (40% weight)
- Brand Loyalty (30% weight)
- Price Sensitivity (30% weight)

### 2. Behavioral Pattern Matching

Analyzes user behavior for personalized recommendations.

**Patterns:**
- Purchase timing preferences
- Product interaction history
- Similar product engagement
- Category interaction frequency

### 3. Session Context Relevance

Considers current session context for immediate relevance.

**Context Factors:**
- Search intent matching (40%)
- Device type optimization (30%)
- Time-of-day relevance (30%)

### 4. Collaborative Filtering

Implements simplified collaborative filtering for enhanced personalization.

**Approach:**
- User similarity based on category preferences
- Price tier matching
- Behavioral pattern clustering

### 5. Temporal Relevance

Adjusts recommendations based on temporal factors.

**Temporal Factors:**
- Seasonal relevance (clothing, gifts)
- Trending product boost
- Time-sensitive promotions

## Geographic Relevance

### Regional Optimization

Adapts search results based on user geographic location.

**Geographic Factors:**

1. **Shipping Optimization**
   - Domestic vs. international shipping
   - Shipping cost consideration
   - Delivery time optimization

2. **Regional Availability**
   - Product availability by region
   - Local inventory levels
   - Regional restrictions

3. **Cultural Preferences**
   - Regional popularity trends
   - Local brand preferences
   - Currency and pricing display

4. **Language Localization**
   - Language-specific content matching
   - Localized product descriptions
   - Cultural context understanding

## A/B Testing Framework

### Algorithm Variants

The system supports multiple ranking algorithms for A/B testing:

1. **Similarity First** (70% similarity, 20% business, 10% personalization)
2. **Business First** (30% similarity, 50% business, 20% personalization)
3. **Balanced** (40% similarity, 30% business, 30% personalization)
4. **Personalized** (20% similarity, 30% business, 50% personalization)
5. **Geographic** (40% similarity, 20% business, 20% personalization, 20% geographic)
6. **Experimental** (30% similarity, 40% business, 20% personalization, 10% experimental)

### Test Assignment

Users are consistently assigned to test groups based on:
- User ID hash (for registered users)
- Session ID hash (for anonymous users)
- Even distribution across algorithm variants

### Performance Tracking

**Metrics Tracked:**
- Click-through Rate (CTR)
- Conversion Rate
- Engagement Rate
- Position-based metrics
- Revenue per search

**Analytics:**
```python
def get_test_performance(algorithm, metric):
    if metric == "ctr":
        clicks = count_interactions(algorithm, "click")
        views = count_interactions(algorithm, "view")
        return clicks / views
    elif metric == "conversion":
        purchases = count_interactions(algorithm, "purchase")
        clicks = count_interactions(algorithm, "click")
        return purchases / clicks
```

## Integration Guide

### 1. Service Integration

The `AdvancedSearchIntegration` service provides high-level integration:

```python
# Initialize advanced search
advanced_search = AdvancedSearchIntegration(enhanced_search_service, vector_service)

# Perform advanced text search
result = await advanced_search.advanced_text_search(
    request=search_request,
    user_context=user_context,
    geographic_context=geo_context,
    session_id=session_id
)
```

### 2. User Context Extraction

User context is automatically extracted from request headers:

```python
async def _extract_user_context(request, current_user):
    return {
        "user_id": current_user.get("user_id"),
        "device_type": detect_device_type(request.headers),
        "preferences": extract_preferences(current_user),
        "level": current_user.get("level")
    }
```

### 3. Geographic Context Extraction

Geographic context uses request headers and IP-based detection:

```python
async def _extract_geographic_context(request):
    return {
        "country": request.headers.get("cf-ipcountry", "US"),
        "language": parse_accept_language(request.headers),
        "currency": map_country_to_currency(country),
        "shipping_zones": determine_shipping_zones(country)
    }
```

## Performance Optimization

### 1. Caching Strategy

**Multi-level Caching:**
- User profile cache (Redis, 1 hour TTL)
- Geographic context cache (Redis, 6 hours TTL)
- Algorithm weights cache (Memory, session-based)
- Product similarity cache (Redis, 24 hours TTL)

### 2. Async Processing

All similarity calculations and business logic evaluations run asynchronously:

```python
async def _calculate_product_score(query_data, product, context, weights):
    # Parallel calculation of different score components
    similarity_task = asyncio.create_task(calculate_similarity_scores(...))
    business_task = asyncio.create_task(calculate_business_score(...))
    personalization_task = asyncio.create_task(calculate_personalization_score(...))
    
    # Wait for all tasks to complete
    similarity_scores, business_score, personalization_score = await asyncio.gather(
        similarity_task, business_task, personalization_task
    )
```

### 3. Batch Processing

When processing multiple products, calculations are batched for efficiency:

```python
# Vectorized similarity calculations
similarities = np.dot(query_embeddings, product_embeddings.T)
enhanced_similarities = 1 / (1 + np.exp(-10 * (similarities - 0.5)))
```

### 4. Fallback Mechanisms

Graceful degradation when advanced features fail:

```python
try:
    # Advanced search with all features
    results = await advanced_search.search_and_rank(...)
except Exception as e:
    logger.warning(f"Advanced search failed: {e}")
    # Fall back to basic search
    results = await basic_search.search(...)
```

## Testing and Validation

### 1. Unit Tests

Comprehensive unit tests cover all components:

```python
class TestSimilarityCalculator:
    def test_visual_similarity_identical_embeddings(self):
        embedding = np.random.rand(512)
        similarity = calculator.calculate_visual_similarity(embedding, embedding)
        assert similarity > 0.9
    
    def test_textual_similarity_exact_match(self):
        similarity = calculator.calculate_textual_similarity(
            "red shoes", "red shoes for running", metadata
        )
        assert similarity > 0.7
```

### 2. Integration Tests

End-to-end testing of the complete search pipeline:

```python
@pytest.mark.asyncio
async def test_advanced_search_integration():
    result = await advanced_search.advanced_text_search(
        request=search_request,
        user_context=user_context,
        session_id="test_session"
    )
    assert result["success"] == True
    assert len(result["products"]) > 0
```

### 3. Performance Tests

Load testing and performance validation:

```python
def test_search_performance():
    start_time = time.time()
    results = await advanced_search.search_and_rank(...)
    processing_time = time.time() - start_time
    assert processing_time < 0.5  # 500ms SLA
```

### 4. A/B Test Validation

Statistical validation of A/B test results:

```python
def validate_ab_test_results():
    algorithm_a_ctr = get_test_performance("algorithm_a", "ctr")
    algorithm_b_ctr = get_test_performance("algorithm_b", "ctr")
    
    # Chi-square test for statistical significance
    p_value = chi_square_test(algorithm_a_ctr, algorithm_b_ctr)
    assert p_value < 0.05  # 95% confidence
```

## API Usage Examples

### 1. Advanced Text Search

```python
POST /search/text
{
    "query": "running shoes",
    "limit": 20,
    "category": "footwear"
}

# Response includes algorithm metadata
{
    "products": [...],
    "search_metadata": {
        "algorithm_used": "personalized",
        "processing_time_ms": 234,
        "personalized": true,
        "geographic_context": true
    }
}
```

### 2. Interaction Tracking

```python
POST /search/interaction
{
    "session_id": "session_123",
    "product_id": "product_456",
    "interaction_type": "click",
    "position": 3,
    "query": "running shoes",
    "algorithm": "balanced"
}
```

### 3. Performance Analytics

```python
GET /search/analytics/performance

# Response (Enterprise users only)
{
    "algorithm_performance": {
        "balanced": {
            "ctr": {"ctr": 0.045, "sample_size": 1250},
            "conversion": {"conversion_rate": 0.023, "sample_size": 567}
        },
        "personalized": {
            "ctr": {"ctr": 0.052, "sample_size": 1189},
            "conversion": {"conversion_rate": 0.029, "sample_size": 618}
        }
    },
    "recommendations": [
        "Algorithm 'personalized' shows best CTR performance (0.052)",
        "Algorithm 'personalized' shows best conversion rate (0.029)"
    ]
}
```

## Configuration

### Environment Variables

```bash
# Advanced Search Configuration
ADVANCED_SEARCH_ENABLED=true
AB_TESTING_ENABLED=true
PERSONALIZATION_ENABLED=true
GEOGRAPHIC_OPTIMIZATION_ENABLED=true

# Performance Settings
SEARCH_TIMEOUT_MS=500
MAX_CANDIDATES_FOR_RANKING=100
CACHE_TTL_SECONDS=3600

# A/B Testing
AB_TEST_ALGORITHMS=balanced,personalized,business_first
DEFAULT_ALGORITHM=balanced
```

### Algorithm Weights Configuration

```json
{
    "similarity_first": {
        "similarity_weight": 0.7,
        "business_weight": 0.2,
        "personalization_weight": 0.1
    },
    "balanced": {
        "similarity_weight": 0.4,
        "business_weight": 0.3,
        "personalization_weight": 0.3
    },
    "personalized": {
        "similarity_weight": 0.2,
        "business_weight": 0.3,
        "personalization_weight": 0.5
    }
}
```

## Monitoring and Alerts

### Key Metrics

1. **Search Performance**
   - Average response time
   - Success rate
   - Error rate by algorithm

2. **Business Metrics**
   - Click-through rate
   - Conversion rate
   - Revenue per search

3. **User Experience**
   - Search abandonment rate
   - Result relevance scores
   - User satisfaction ratings

### Alerting Rules

```yaml
alerts:
  - name: "High Search Latency"
    condition: "avg_search_time_ms > 1000"
    threshold: "5 minutes"
    
  - name: "Low CTR"
    condition: "ctr < 0.02"
    threshold: "1 hour"
    
  - name: "Algorithm Performance Degradation"
    condition: "conversion_rate_drop > 0.005"
    threshold: "2 hours"
```

This advanced search implementation provides a comprehensive, production-ready solution that combines multiple sophisticated algorithms to deliver highly relevant, personalized search results while maintaining excellent performance and providing detailed analytics for continuous optimization.
