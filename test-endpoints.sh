#!/bin/bash
# Quick verification script to test API endpoints

echo "🧪 Testing API Endpoints..."
echo ""

BASE_URL="http://localhost:8001"

echo "1️⃣  Testing /api/campaigns"
curl -s "$BASE_URL/api/campaigns" | jq -r 'if type=="array" then "✅ Campaigns endpoint OK (\(length) items)" else "❌ Error: \(.)" end'

echo ""
echo "2️⃣  Testing /api/leads"
curl -s "$BASE_URL/api/leads" | jq -r 'if type=="array" then "✅ Leads endpoint OK (\(length) items)" else "❌ Error: \(.)" end'

echo ""
echo "3️⃣  Testing /api/dashboard/stats"
curl -s "$BASE_URL/api/dashboard/stats" | jq -r 'if .campaigns and .leads then "✅ Dashboard stats OK" else "❌ Error" end'

echo ""
echo "4️⃣  Testing trailing slash handling (should not redirect)"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/campaigns")
if [ "$HTTP_CODE" == "200" ]; then
  echo "✅ No trailing slash: $HTTP_CODE"
else
  echo "❌ No trailing slash returned: $HTTP_CODE (expected 200)"
fi

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/campaigns/")
if [ "$HTTP_CODE" == "200" ]; then
  echo "✅ With trailing slash: $HTTP_CODE"
else
  echo "❌ With trailing slash returned: $HTTP_CODE (expected 200)"
fi

echo ""
echo "5️⃣  Frontend accessibility"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000")
if [ "$HTTP_CODE" == "200" ]; then
  echo "✅ Frontend accessible at http://localhost:3000"
else
  echo "❌ Frontend returned: $HTTP_CODE"
fi

echo ""
echo "📋 Summary:"
echo "   - Backend API: http://localhost:8001"
echo "   - Frontend UI: http://localhost:3000"
echo "   - API Docs: http://localhost:8001/docs"
echo ""
echo "🎯 Next steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Clear browser cache (Cmd+Shift+R or Ctrl+Shift+R)"
echo "   3. Navigate to Campaigns and Leads pages"
echo "   4. Check browser Network tab - all requests should be to /api/* (relative)"
echo ""

