BASE_URL="http://localhost:8080"

echo "=== Testing Python Execution API ==="

echo -e "\n1. Health Check:"
curl -s "$BASE_URL/health" | python3 -m json.tool

echo -e "\n2. Simple Calculation:"
curl -s -X POST "$BASE_URL/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    return {\"result\": 2 + 2, \"message\": \"success\"}"
  }' | python3 -m json.tool

echo -e "\n3. With Print Statements:"
curl -s -X POST "$BASE_URL/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    print(\"Calculating...\")\n    result = sum([1, 2, 3, 4, 5])\n    print(f\"Sum: {result}\")\n    return {\"total\": result}"
  }' | python3 -m json.tool

echo -e "\n4. Pandas and NumPy:"
curl -s -X POST "$BASE_URL/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    import pandas as pd\n    import numpy as np\n    data = pd.DataFrame({\"x\": [1,2,3], \"y\": [4,5,6]})\n    return {\"mean_x\": float(np.mean(data[\"x\"])), \"shape\": list(data.shape)}"
  }' | python3 -m json.tool

echo -e "\n5. Error Test - No main function:"
curl -s -X POST "$BASE_URL/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "script": "print(\"This script has no main function\")"
  }' | python3 -m json.tool

echo -e "\n6. Error Test - Dangerous code:"
curl -s -X POST "$BASE_URL/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "script": "import os\ndef main():\n    return os.listdir(\"/\")"
  }' | python3 -m json.tool

echo -e "\n=== Testing Complete ==="
