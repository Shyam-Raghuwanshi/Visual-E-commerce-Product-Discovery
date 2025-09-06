import React, { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription } from '../ui/alert';
import { Star, Heart, ShoppingCart, Sparkles, TrendingUp, Leaf, Users, Crown } from 'lucide-react';

const DemoScenariosShowcase = () => {
  const [activeDemo, setActiveDemo] = useState('celebrity');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  // Demo scenario configurations
  const demoScenarios = {
    celebrity: {
      title: "Celebrity Outfit Recreation",
      icon: <Crown className="w-5 h-5" />,
      description: "Get this red carpet look",
      color: "bg-purple-500",
    },
    budget: {
      title: "Budget-Conscious Shopping",
      icon: <ShoppingCart className="w-5 h-5" />,
      description: "Luxury look for less",
      color: "bg-green-500",
    },
    sustainable: {
      title: "Sustainable Fashion",
      icon: <Leaf className="w-5 h-5" />,
      description: "Eco-friendly alternatives",
      color: "bg-emerald-500",
    },
    sizeInclusive: {
      title: "Size-Inclusive Options",
      icon: <Users className="w-5 h-5" />,
      description: "Find this in my size",
      color: "bg-blue-500",
    },
    trends: {
      title: "Trend Forecasting",
      icon: <TrendingUp className="w-5 h-5" />,
      description: "What's coming next season",
      color: "bg-orange-500",
    }
  };

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

  const runDemo = async (demoType, params = {}) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      let endpoint = '';
      let requestBody = {};

      switch (demoType) {
        case 'celebrity':
          endpoint = '/api/demo/celebrity-outfit-recreation';
          requestBody = {
            celebrity_name: params.celebrity || null,
            budget_range: params.budget ? { min: 0, max: params.budget } : null
          };
          break;
        case 'budget':
          endpoint = '/api/demo/budget-conscious-shopping';
          requestBody = {
            target_look: params.targetLook || 'elegant evening wear',
            max_budget: params.maxBudget || 200,
            style_preferences: params.stylePreferences || []
          };
          break;
        case 'sustainable':
          endpoint = '/api/demo/sustainable-fashion-alternatives';
          requestBody = {
            search_query: params.searchQuery || 'dress',
            sustainability_criteria: params.criteria || []
          };
          break;
        case 'sizeInclusive':
          endpoint = '/api/demo/size-inclusive-search';
          requestBody = {
            search_query: params.searchQuery || 'dress',
            target_size: params.targetSize || 'M'
          };
          break;
        case 'trends':
          endpoint = '/api/demo/trend-forecasting';
          requestBody = {
            season: params.season || null,
            year: params.year || null
          };
          break;
        default:
          throw new Error('Unknown demo type');
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message || 'An error occurred while running the demo');
      console.error('Demo error:', err);
    } finally {
      setLoading(false);
    }
  };

  const CelebrityDemo = () => {
    const [celebrity, setCelebrity] = useState('');
    const [budget, setBudget] = useState('');

    const handleRun = () => {
      runDemo('celebrity', { 
        celebrity: celebrity || null, 
        budget: budget ? parseFloat(budget) : null 
      });
    };

    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="celebrity">Celebrity (Optional)</Label>
            <Input
              id="celebrity"
              placeholder="e.g., Emma Stone, Zendaya"
              value={celebrity}
              onChange={(e) => setCelebrity(e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="budget">Budget Limit (Optional)</Label>
            <Input
              id="budget"
              type="number"
              placeholder="e.g., 500"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
            />
          </div>
        </div>
        <Button onClick={handleRun} disabled={loading} className="w-full">
          {loading ? 'Creating Look...' : 'Get Celebrity Look'}
        </Button>
      </div>
    );
  };

  const BudgetDemo = () => {
    const [targetLook, setTargetLook] = useState('elegant evening wear');
    const [maxBudget, setMaxBudget] = useState(200);

    const handleRun = () => {
      runDemo('budget', { targetLook, maxBudget });
    };

    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="targetLook">Target Look</Label>
            <Input
              id="targetLook"
              placeholder="e.g., elegant evening wear"
              value={targetLook}
              onChange={(e) => setTargetLook(e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="maxBudget">Maximum Budget ($)</Label>
            <Input
              id="maxBudget"
              type="number"
              value={maxBudget}
              onChange={(e) => setMaxBudget(parseFloat(e.target.value))}
            />
          </div>
        </div>
        <Button onClick={handleRun} disabled={loading} className="w-full">
          {loading ? 'Finding Deals...' : 'Find Budget Options'}
        </Button>
      </div>
    );
  };

  const SustainableDemo = () => {
    const [searchQuery, setSearchQuery] = useState('dress');

    const handleRun = () => {
      runDemo('sustainable', { searchQuery });
    };

    return (
      <div className="space-y-4">
        <div>
          <Label htmlFor="searchQuery">Search for</Label>
          <Input
            id="searchQuery"
            placeholder="e.g., dress, jeans, sweater"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Button onClick={handleRun} disabled={loading} className="w-full">
          {loading ? 'Finding Eco Options...' : 'Find Sustainable Alternatives'}
        </Button>
      </div>
    );
  };

  const SizeInclusiveDemo = () => {
    const [searchQuery, setSearchQuery] = useState('dress');
    const [targetSize, setTargetSize] = useState('M');

    const handleRun = () => {
      runDemo('sizeInclusive', { searchQuery, targetSize });
    };

    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="searchQuery">Search for</Label>
            <Input
              id="searchQuery"
              placeholder="e.g., dress, jeans, sweater"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="targetSize">Your Size</Label>
            <select
              id="targetSize"
              className="w-full p-2 border rounded"
              value={targetSize}
              onChange={(e) => setTargetSize(e.target.value)}
            >
              <option value="XS">XS</option>
              <option value="S">S</option>
              <option value="M">M</option>
              <option value="L">L</option>
              <option value="XL">XL</option>
              <option value="XXL">XXL</option>
              <option value="XXXL">XXXL</option>
            </select>
          </div>
        </div>
        <Button onClick={handleRun} disabled={loading} className="w-full">
          {loading ? 'Checking Sizes...' : 'Find in My Size'}
        </Button>
      </div>
    );
  };

  const TrendsDemo = () => {
    const [season, setSeason] = useState('');
    const [year, setYear] = useState('');

    const handleRun = () => {
      runDemo('trends', { 
        season: season || null, 
        year: year ? parseInt(year) : null 
      });
    };

    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="season">Season (Optional)</Label>
            <select
              id="season"
              className="w-full p-2 border rounded"
              value={season}
              onChange={(e) => setSeason(e.target.value)}
            >
              <option value="">Any Season</option>
              <option value="Spring">Spring</option>
              <option value="Summer">Summer</option>
              <option value="Fall">Fall</option>
              <option value="Winter">Winter</option>
            </select>
          </div>
          <div>
            <Label htmlFor="year">Year (Optional)</Label>
            <Input
              id="year"
              type="number"
              placeholder="e.g., 2025"
              value={year}
              onChange={(e) => setYear(e.target.value)}
            />
          </div>
        </div>
        <Button onClick={handleRun} disabled={loading} className="w-full">
          {loading ? 'Analyzing Trends...' : 'Predict Trends'}
        </Button>
      </div>
    );
  };

  const renderDemoForm = () => {
    switch (activeDemo) {
      case 'celebrity':
        return <CelebrityDemo />;
      case 'budget':
        return <BudgetDemo />;
      case 'sustainable':
        return <SustainableDemo />;
      case 'sizeInclusive':
        return <SizeInclusiveDemo />;
      case 'trends':
        return <TrendsDemo />;
      default:
        return null;
    }
  };

  const renderResults = () => {
    if (!results || !results.data) return null;

    const data = results.data;

    switch (results.demo_type) {
      case 'celebrity_outfit_recreation':
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Crown className="w-5 h-5 text-purple-500" />
                  {data.celebrity_inspiration.name} - {data.celebrity_inspiration.event}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">{data.celebrity_inspiration.description}</p>
                <div className="flex flex-wrap gap-2 mb-4">
                  {data.celebrity_inspiration.style_tags.map((tag, index) => (
                    <Badge key={index} variant="secondary">{tag}</Badge>
                  ))}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-semibold mb-2">Color Palette</h4>
                    <div className="flex gap-2">
                      {data.celebrity_inspiration.color_palette.map((color, index) => (
                        <div key={index} className="px-3 py-1 bg-gray-100 rounded-full text-sm">
                          {color}
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2">Total Cost</h4>
                    <p className="text-2xl font-bold text-green-600">${data.total_cost.toFixed(2)}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.recreated_outfit.map((piece, index) => (
                <Card key={index}>
                  <CardContent className="p-4">
                    <h4 className="font-semibold mb-2">{piece.original_piece.type}</h4>
                    <img
                      src={piece.suggested_product.image_url}
                      alt={piece.suggested_product.name}
                      className="w-full h-48 object-cover rounded mb-2"
                    />
                    <p className="text-sm text-gray-600 mb-2">{piece.suggested_product.name}</p>
                    <p className="font-bold">${piece.suggested_product.price}</p>
                    <div className="flex items-center gap-1 mt-2">
                      <Star className="w-4 h-4 text-yellow-500" />
                      <span className="text-sm">{(piece.similarity_score * 100).toFixed(0)}% match</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        );

      case 'budget_conscious_shopping':
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ShoppingCart className="w-5 h-5 text-green-500" />
                  Budget Shopping Results for "{data.target_look}"
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">${data.budget_limit}</p>
                    <p className="text-sm text-gray-600">Budget Limit</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">{data.budget_products.length}</p>
                    <p className="text-sm text-gray-600">Options Found</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-purple-600">${data.money_saved.toFixed(2)}</p>
                    <p className="text-sm text-gray-600">Money Saved</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.budget_products.slice(0, 6).map((product, index) => (
                <Card key={index}>
                  <CardContent className="p-4">
                    <img
                      src={product.image_url}
                      alt={product.name}
                      className="w-full h-48 object-cover rounded mb-2"
                    />
                    <h4 className="font-semibold mb-1">{product.name}</h4>
                    <p className="text-sm text-gray-600 mb-2">{product.brand}</p>
                    <p className="font-bold text-green-600">${product.price}</p>
                    <div className="flex items-center gap-1 mt-2">
                      <Star className="w-4 h-4 text-yellow-500" />
                      <span className="text-sm">{product.rating}/5</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        );

      case 'sustainable_fashion_alternatives':
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Leaf className="w-5 h-5 text-green-500" />
                  Sustainable Fashion Alternatives
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">{data.sustainable_alternatives.length}</p>
                    <p className="text-sm text-gray-600">Sustainable Options</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">{data.eco_impact_summary.estimated_water_savings_liters}L</p>
                    <p className="text-sm text-gray-600">Water Saved</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-purple-600">{data.eco_impact_summary.estimated_co2_reduction_kg}kg</p>
                    <p className="text-sm text-gray-600">CO2 Reduced</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.sustainable_alternatives.slice(0, 6).map((item, index) => (
                <Card key={index}>
                  <CardContent className="p-4">
                    <img
                      src={item.product.image_url}
                      alt={item.product.name}
                      className="w-full h-48 object-cover rounded mb-2"
                    />
                    <h4 className="font-semibold mb-1">{item.product.name}</h4>
                    <p className="text-sm text-gray-600 mb-2">{item.product.brand}</p>
                    <p className="font-bold">${item.product.price}</p>
                    <div className="flex items-center gap-1 mt-2">
                      <Leaf className="w-4 h-4 text-green-500" />
                      <span className="text-sm">{item.sustainability_score}% sustainable</span>
                    </div>
                    <div className="mt-2">
                      {item.eco_features.slice(0, 2).map((feature, idx) => (
                        <Badge key={idx} variant="outline" className="text-xs mr-1">
                          {feature}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        );

      case 'size_inclusive_search':
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="w-5 h-5 text-blue-500" />
                  Size {data.target_size} Availability
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">{(data.size_availability_rate * 100).toFixed(0)}%</p>
                    <p className="text-sm text-gray-600">Available in Your Size</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">{data.available_products.length}</p>
                    <p className="text-sm text-gray-600">Products Found</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-purple-600">{data.inclusive_brands.length}</p>
                    <p className="text-sm text-gray-600">Inclusive Brands</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.available_products.slice(0, 6).map((product, index) => (
                <Card key={index}>
                  <CardContent className="p-4">
                    <img
                      src={product.image_url}
                      alt={product.name}
                      className="w-full h-48 object-cover rounded mb-2"
                    />
                    <h4 className="font-semibold mb-1">{product.name}</h4>
                    <p className="text-sm text-gray-600 mb-2">{product.brand}</p>
                    <p className="font-bold">${product.price}</p>
                    <Badge variant="secondary" className="mt-2">Size {product.size}</Badge>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        );

      case 'trend_forecasting':
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-orange-500" />
                  Fashion Trends for {data.forecast_period}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center mb-4">
                  <p className="text-2xl font-bold text-orange-600">{(data.confidence_level * 100).toFixed(0)}%</p>
                  <p className="text-sm text-gray-600">Forecast Confidence</p>
                </div>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {data.predicted_trends.map((trend, index) => (
                <Card key={index}>
                  <CardHeader>
                    <CardTitle className="text-lg">{trend.name}</CardTitle>
                    <Progress value={trend.confidence * 100} className="w-full" />
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div>
                        <h5 className="font-semibold text-sm">Key Elements</h5>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {trend.key_elements.slice(0, 4).map((element, idx) => (
                            <Badge key={idx} variant="outline" className="text-xs">
                              {element}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h5 className="font-semibold text-sm">Colors</h5>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {trend.colors.slice(0, 4).map((color, idx) => (
                            <Badge key={idx} variant="secondary" className="text-xs">
                              {color}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-4">Demo Scenarios Showcase</h1>
        <p className="text-gray-600 text-lg">
          Experience next-generation fashion discovery with AI-powered scenarios
        </p>
      </div>

      {/* Demo Selection */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
        {Object.entries(demoScenarios).map(([key, scenario]) => (
          <Button
            key={key}
            variant={activeDemo === key ? "default" : "outline"}
            className={`p-4 h-auto flex flex-col items-center gap-2 ${
              activeDemo === key ? scenario.color : ''
            }`}
            onClick={() => setActiveDemo(key)}
          >
            {scenario.icon}
            <div className="text-center">
              <div className="font-semibold text-sm">{scenario.title}</div>
              <div className="text-xs opacity-80">{scenario.description}</div>
            </div>
          </Button>
        ))}
      </div>

      {/* Demo Forms */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {demoScenarios[activeDemo].icon}
            {demoScenarios[activeDemo].title}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {renderDemoForm()}
        </CardContent>
      </Card>

      {/* Loading State */}
      {loading && (
        <Card className="mb-8">
          <CardContent className="p-8 text-center">
            <div className="flex items-center justify-center gap-3">
              <Sparkles className="w-6 h-6 animate-spin text-blue-500" />
              <span className="text-lg">Running AI-powered demo...</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error State */}
      {error && (
        <Alert className="mb-8">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Results */}
      {results && !loading && (
        <div>
          <h2 className="text-2xl font-bold mb-6">Demo Results</h2>
          {renderResults()}
        </div>
      )}
    </div>
  );
};

export default DemoScenariosShowcase;
