#!/bin/bash
# MongoDB News Query Script

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Helper function to run mongosh with Atlas
run_mongosh() {
    local db=$1
    local cmd=$2
    if [ -z "$MONGODB_URI" ]; then
        echo -e "${YELLOW}⚠️  MONGODB_URI not set. Using environment from backend/.env${NC}"
        if [ -f backend/.env ]; then
            export $(cat backend/.env | grep MONGODB_URI | xargs)
        fi
    fi
    
    if [ -z "$MONGODB_URI" ]; then
        echo -e "${YELLOW}❌ MONGODB_URI not found. Please set it:${NC}"
        echo "export MONGODB_URI='mongodb+srv://user:pass@cluster.mongodb.net/'"
        return 1
    fi
    
    mongosh "$MONGODB_URI/$db" --quiet --eval "$cmd" 2>/dev/null || {
        echo -e "${YELLOW}❌ Failed to connect to MongoDB Atlas${NC}"
        echo "Check your MONGODB_URI and network connection"
        return 1
    }
}

show_help() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}           MongoDB News Database Query Tool                  ${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Note: Using MongoDB Atlas (remote database)${NC}"
    echo -e "${YELLOW}   Most commands require mongosh with Atlas connection string${NC}"
    echo -e "${YELLOW}   Set MONGODB_URI env var or pass connection string manually${NC}"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  stats              - Show database statistics (via API)"
    echo "  dedup              - Show deduplication statistics from logs"
    echo "  recent [N]         - Show N most recent enriched articles (requires mongosh)"
    echo "  company [name]     - Show articles for specific company (requires mongosh)"
    echo "  sentiment [label]  - Show articles by sentiment (requires mongosh)"
    echo "  clusters           - Show story clusters (requires mongosh)"
    echo "  events             - Show articles with critical events (requires mongosh)"
    echo "  article [url]      - Show full article details by URL (requires mongosh)"
    echo "  throughput         - Show article processing throughput (requires mongosh)"
    echo ""
    echo "Examples:"
    echo "  $0 stats                    # Uses API (no mongosh needed)"
    echo "  $0 dedup                    # Uses docker logs (no mongosh needed)"
    echo "  MONGODB_URI='mongodb+srv://...' $0 recent 10"
    echo "  MONGODB_URI='mongodb+srv://...' $0 company britannia"
    echo ""
}

# Parse command
COMMAND=${1:-help}

case $COMMAND in
    dedup)
        echo -e "${YELLOW}🔍 Deduplication Statistics:${NC}"
        echo ""
        
        # Get enrichment-pipeline container logs
        LOGS=$(docker logs enrichment-pipeline 2>&1 | tail -1000)
        
        # Count different types
        URL_DUPS=$(echo "$LOGS" | grep -c "⊘ URL duplicate:" || true)
        CONTENT_DUPS=$(echo "$LOGS" | grep -c "⊘ Content duplicate:" || true)
        TITLE_DUPS=$(echo "$LOGS" | grep -c "⊕ Title duplicate" || true)
        UNIQUE=$(echo "$LOGS" | grep -c "✓ UNIQUE enriched:" || true)
        
        TOTAL=$((URL_DUPS + CONTENT_DUPS + TITLE_DUPS + UNIQUE))
        
        echo "📊 Processing Summary (last 1000 log entries):"
        echo "  Total processed:       $TOTAL articles"
        echo ""
        echo "✓ Unique articles:       $UNIQUE ($(awk "BEGIN {printf \"%.1f\", $UNIQUE*100.0/$TOTAL}")%)"
        echo ""
        echo "⊘ Duplicates filtered:   $((TOTAL - UNIQUE)) ($(awk "BEGIN {printf \"%.1f\", ($TOTAL-$UNIQUE)*100.0/$TOTAL}")%)"
        echo "  ├─ URL duplicates:     $URL_DUPS"
        echo "  ├─ Content duplicates: $CONTENT_DUPS"
        echo "  └─ Title duplicates:   $TITLE_DUPS (merged to clusters)"
        echo ""
        
        # Show recent duplicates
        echo -e "${BLUE}Recent Duplicate Examples:${NC}"
        echo "$LOGS" | grep -E "(⊘|⊕)" | tail -10
        echo ""
        
        # Show recent unique
        echo -e "${GREEN}Recent Unique Articles:${NC}"
        echo "$LOGS" | grep "✓ UNIQUE enriched:" | tail -5
        ;;
    
    stats)
        echo -e "${YELLOW}📊 Database Statistics:${NC}"
        echo -e "${BLUE}Using API endpoint (MongoDB Atlas):${NC}"
        curl -s http://localhost:8000/api/news/stats | python3 -m json.tool
        echo ""
        echo -e "${BLUE}Detailed MongoDB queries (requires mongosh + Atlas connection string):${NC}"
        echo "Run: mongosh 'your-atlas-connection-string' --eval \"
        print('\\n📰 Collections Overview:');
        print('  Raw Articles: ' + db.raw_articles.countDocuments());
        print('  Enriched Articles: ' + db.enriched_articles.countDocuments());
        print('  Story Clusters: ' + db.story_clusters.countDocuments());
        
        print('\\n🏢 Articles by Company:');
        db.enriched_articles.aggregate([
            { \$group: { _id: '\$company', count: { \$sum: 1 } } },
            { \$sort: { count: -1 } }
        ]).forEach(doc => print('  ' + doc._id + ': ' + doc.count));
        
        print('\\n😊 Sentiment Distribution:');
        db.enriched_articles.aggregate([
            { \$group: { _id: '\$sentiment_label', count: { \$sum: 1 } } },
            { \$sort: { count: -1 } }
        ]).forEach(doc => print('  ' + doc._id + ': ' + doc.count));
        
        print('\\n📂 Factor Types:');
        db.enriched_articles.aggregate([
            { \$group: { _id: '\$factor_type', count: { \$sum: 1 } } },
            { \$sort: { count: -1 } }
        ]).forEach(doc => print('  ' + doc._id + ': ' + doc.count));
        
        print('\\n🎯 Liquidity Impact:');
        db.enriched_articles.aggregate([
            { \$group: { _id: '\$liquidity_impact', count: { \$sum: 1 } } },
            { \$sort: { count: -1 } }
        ]).forEach(doc => print('  ' + doc._id + ': ' + doc.count));
        "
        ;;
    
    recent)
        LIMIT=${2:-5}
        echo -e "${YELLOW}📰 Most Recent $LIMIT Enriched Articles:${NC}"
        run_mongosh "news_db" "
        db.enriched_articles.find().sort({ published_at: -1 }).limit($LIMIT).forEach(doc => {
            print('\\n─────────────────────────────────────────────────────────────');
            print('📌 ' + doc.title);
            print('🏢 Company: ' + doc.company + ' | Factor: ' + doc.factor_type);
            print('📰 Publisher: ' + (doc.publisher_name || 'N/A') + ' | Author: ' + (doc.author || 'N/A'));
            print('📅 Published: ' + doc.published_at);
            print('😊 Sentiment: ' + doc.sentiment_label + ' (' + doc.sentiment_score.toFixed(2) + ')');
            print('💧 Liquidity: ' + doc.liquidity_impact);
            print('🔗 URL: ' + doc.url);
            print('🔑 Events: ' + doc.critical_events);
            print('📊 Decisions: ' + doc.decisions);
            if (doc.summary) print('📝 Summary: ' + doc.summary.substring(0, 200) + '...');
        });
        "
        ;;
    
    company)
        COMPANY=${2:-britannia}
        echo -e "${YELLOW}🏢 Articles for Company: $COMPANY${NC}"
        run_mongosh "news_db" "
        const count = db.enriched_articles.countDocuments({ company: '$COMPANY' });
        print('Total articles: ' + count + '\\n');
        
        db.enriched_articles.find({ company: '$COMPANY' }).sort({ published_at: -1 }).limit(5).forEach(doc => {
            print('─────────────────────────────────────────────────────────────');
            print('📌 ' + doc.title);
            print('😊 Sentiment: ' + doc.sentiment_label + ' (' + doc.sentiment_score.toFixed(2) + ')');
            print('📅 Published: ' + doc.published_at);
            print('💧 Liquidity: ' + doc.liquidity_impact);
            print('🔗 URL: ' + doc.url);
            print('');
        });
        "
        ;;
    
    sentiment)
        SENTIMENT=${2:-positive}
        echo -e "${YELLOW}😊 Articles with Sentiment: $SENTIMENT${NC}"
        run_mongosh "news_db" "
        const count = db.enriched_articles.countDocuments({ sentiment_label: '$SENTIMENT' });
        print('Total articles: ' + count + '\\n');
        
        db.enriched_articles.find({ sentiment_label: '$SENTIMENT' }).sort({ sentiment_score: -1 }).limit(5).forEach(doc => {
            print('─────────────────────────────────────────────────────────────');
            print('📌 ' + doc.title);
            print('🏢 Company: ' + doc.company);
            print('😊 Score: ' + doc.sentiment_score.toFixed(3) + ' (' + doc.sentiment_confidence + ')');
            print('📅 Published: ' + doc.published_at);
            print('🔗 URL: ' + doc.url);
            print('');
        });
        "
        ;;
    
    clusters)
        echo -e "${YELLOW}🗂️  Story Clusters:${NC}"
        run_mongosh "news_db" "
        db.story_clusters.find().sort({ last_updated: -1 }).limit(10).forEach(doc => {
            print('\\n─────────────────────────────────────────────────────────────');
            print('🆔 Cluster: ' + doc.cluster_id);
            print('📌 Title: ' + doc.title);
            print('🏢 Company: ' + doc.company + ' | Factor: ' + doc.factor_type);
            print('📰 Articles: ' + doc.article_count);
            print('📡 Sources: ' + doc.sources.join(', '));
            print('😊 Sentiment: ' + doc.sentiment_label + ' (' + doc.sentiment_score.toFixed(2) + ')');
            print('💧 Liquidity: ' + doc.liquidity_impact);
            print('📅 Last Updated: ' + doc.last_updated);
            if (doc.publishers && doc.publishers.length > 0) {
                print('\\n📰 Publishers covering this story:');
                doc.publishers.forEach(pub => {
                    print('  • ' + pub.name + ' (' + pub.source + ')');
                    if (pub.icon) print('    Icon: ' + pub.icon);
                });
            }
        });
        "
        ;;
    
    events)
        echo -e "${YELLOW}🚨 Articles with Critical Events:${NC}"
        run_mongosh "news_db" "
        db.enriched_articles.find({ 
            critical_events: { \$ne: '' } 
        }).sort({ published_at: -1 }).limit(10).forEach(doc => {
            print('\\n─────────────────────────────────────────────────────────────');
            print('📌 ' + doc.title);
            print('🏢 Company: ' + doc.company);
            print('🚨 Events: ' + doc.critical_events);
            print('📊 Decisions: ' + doc.decisions);
            print('😊 Sentiment: ' + doc.sentiment_label + ' (' + doc.sentiment_score.toFixed(2) + ')');
            print('📅 Published: ' + doc.published_at);
            print('🔗 URL: ' + doc.url);
        });
        "
        ;;
    
    throughput)
        echo -e "${YELLOW}⚡ Article Processing Throughput:${NC}"
        run_mongosh "news_db" "
        print('\\n📊 Pipeline Throughput Analysis\\n');

        function percentile(sorted, p) {
            if (!sorted.length) return null;
            var idx = (sorted.length - 1) * p;
            var lo = Math.floor(idx);
            var hi = Math.ceil(idx);
            if (lo === hi) return sorted[lo];
            return sorted[lo] + (sorted[hi] - sorted[lo]) * (idx - lo);
        }

        function formatDuration(seconds) {
            if (seconds < 60) return seconds.toFixed(2) + 's';
            if (seconds < 3600) return (seconds / 60).toFixed(2) + 'm';
            return (seconds / 3600).toFixed(2) + 'h';
        }

        function analyzeWindow(windowMs, label) {
            var now = Date.now();
            var windowStart = new Date(now - windowMs);
            print('━━━ ' + label + ' ━━━');

            // Get enriched articles in this window (by enriched_at)
            var docs = db.enriched_articles.find({ 
                enriched_at: { \$gte: windowStart.toISOString() } 
            }).sort({ enriched_at: 1 }).toArray();
            
            var count = docs.length;
            if (count === 0) {
                print('  No articles enriched in this window\\n');
                return;
            }

            // Calculate enrichment latency: scraped_at → enriched_at
            var enrichLatencies = [];
            var enrichedTimes = [];
            
            docs.forEach(d => {
                if (d.enriched_at) {
                    enrichedTimes.push(new Date(d.enriched_at).getTime());
                }
                if (d.scraped_at && d.enriched_at) {
                    var start = new Date(d.scraped_at).getTime();
                    var end = new Date(d.enriched_at).getTime();
                    if (end >= start) {
                        enrichLatencies.push((end - start) / 1000.0);
                    }
                }
            });

            print('  📰 Articles enriched: ' + count);
            
            // Calculate burst-based metrics (ignore idle gaps > 30s)
            if (count > 1) {
                var IDLE_THRESHOLD = 30000; // 30 seconds in ms
                var bursts = [];
                var currentBurst = { start: enrichedTimes[0], end: enrichedTimes[0], count: 1 };
                
                for (var i = 1; i < enrichedTimes.length; i++) {
                    var gap = enrichedTimes[i] - enrichedTimes[i-1];
                    
                    if (gap <= IDLE_THRESHOLD) {
                        // Continue current burst
                        currentBurst.end = enrichedTimes[i];
                        currentBurst.count++;
                    } else {
                        // Gap too large, end current burst and start new one
                        if (currentBurst.count > 0) {
                            bursts.push(currentBurst);
                        }
                        currentBurst = { start: enrichedTimes[i], end: enrichedTimes[i], count: 1 };
                    }
                }
                // Add last burst
                if (currentBurst.count > 0) {
                    bursts.push(currentBurst);
                }
                
                // Calculate metrics
                var totalBurstTime = 0;
                var totalArticles = 0;
                bursts.forEach(b => {
                    totalBurstTime += (b.end - b.start) / 1000.0;
                    totalArticles += b.count;
                });
                
                // Add 1 second per burst (minimum processing time)
                totalBurstTime += bursts.length;
                
                var avgThroughput = totalArticles / totalBurstTime;
                var totalSpan = (enrichedTimes[enrichedTimes.length - 1] - enrichedTimes[0]) / 1000.0;
                
                print('  ⚡ Peak throughput: ' + avgThroughput.toFixed(3) + ' articles/sec (' + (avgThroughput * 60).toFixed(1) + '/min, ' + (avgThroughput * 3600).toFixed(0) + '/hour)');
                print('  ⏱️  Active processing: ' + formatDuration(totalBurstTime) + ' across ' + bursts.length + ' burst(s)');
                print('  📊 Total span: ' + formatDuration(totalSpan) + ' (includes idle time between bursts)');
                
                if (bursts.length > 1) {
                    print('  🔥 Largest burst: ' + bursts.reduce((max, b) => b.count > max ? b.count : max, 0) + ' articles');
                }
            } else if (count === 1) {
                print('  ⚡ Single article (no throughput calc)');
            }

            if (enrichLatencies.length > 0) {
                enrichLatencies.sort(function(a,b){return a-b;});
                var avg = enrichLatencies.reduce((a,b)=>a+b,0) / enrichLatencies.length;
                var p50 = percentile(enrichLatencies, 0.50);
                var p95 = percentile(enrichLatencies, 0.95);
                var p99 = percentile(enrichLatencies, 0.99);
                print('  🔄 Enrich latency (scraped → enriched):');
                print('     Avg: ' + avg.toFixed(2) + 's | P50: ' + p50.toFixed(2) + 's | P95: ' + p95.toFixed(2) + 's | P99: ' + p99.toFixed(2) + 's');
            }

            // Summarization latency: enriched_at → summarized_at
            var sumLatencies = [];
            docs.forEach(d => {
                if (d.enriched_at && d.summarized_at) {
                    var start = new Date(d.enriched_at).getTime();
                    var end = new Date(d.summarized_at).getTime();
                    if (end >= start) {
                        sumLatencies.push((end - start) / 1000.0);
                    }
                }
            });

            if (sumLatencies.length > 0) {
                sumLatencies.sort(function(a,b){return a-b;});
                var avgS = sumLatencies.reduce((a,b)=>a+b,0) / sumLatencies.length;
                var p50S = percentile(sumLatencies, 0.50);
                var p95S = percentile(sumLatencies, 0.95);
                print('  🤖 LLM latency (enriched → summarized):');
                print('     Avg: ' + avgS.toFixed(2) + 's | P50: ' + p50S.toFixed(2) + 's | P95: ' + p95S.toFixed(2) + 's');
                print('     Summarized: ' + sumLatencies.length + '/' + count + ' articles');
            }

            // End-to-end latency: scraped_at → summarized_at
            var e2eLatencies = [];
            docs.forEach(d => {
                if (d.scraped_at && d.summarized_at) {
                    var start = new Date(d.scraped_at).getTime();
                    var end = new Date(d.summarized_at).getTime();
                    if (end >= start) {
                        e2eLatencies.push((end - start) / 1000.0);
                    }
                }
            });

            if (e2eLatencies.length > 0) {
                e2eLatencies.sort(function(a,b){return a-b;});
                var avgE = e2eLatencies.reduce((a,b)=>a+b,0) / e2eLatencies.length;
                var p50E = percentile(e2eLatencies, 0.50);
                var p95E = percentile(e2eLatencies, 0.95);
                print('  🏁 End-to-end (scraped → summarized):');
                print('     Avg: ' + avgE.toFixed(2) + 's | P50: ' + p50E.toFixed(2) + 's | P95: ' + p95E.toFixed(2) + 's');
            }

            print('');
        }

        // Analyze different time windows
        analyzeWindow(5 * 60 * 1000, 'Last 5 minutes');
        analyzeWindow(60 * 60 * 1000, 'Last 1 hour');
        analyzeWindow(24 * 60 * 60 * 1000, 'Last 24 hours');

        // Overall stats
        print('━━━ Overall Stats ━━━');
        var total = db.enriched_articles.countDocuments();
        var summarized = db.enriched_articles.countDocuments({ summarized_at: { \$exists: true } });
        print('  Total enriched: ' + total);
        print('  Total summarized: ' + summarized);
        
        // Find first and last articles
        var first = db.enriched_articles.findOne({}, { sort: { scraped_at: 1 } });
        var last = db.enriched_articles.findOne({}, { sort: { scraped_at: -1 } });
        if (first && last && first.scraped_at && last.scraped_at) {
            print('  First scraped: ' + first.scraped_at);
            print('  Last scraped: ' + last.scraped_at);
        }
        "
        ;;
    
    article)
        if [ -z "$2" ]; then
            echo "Error: Please provide article URL"
            echo "Usage: $0 article <url>"
            exit 1
        fi
        URL="$2"
        echo -e "${YELLOW}📄 Article Details:${NC}"
        run_mongosh "news_db" "
        const article = db.enriched_articles.findOne({ url: '$URL' });
        if (article) {
            print('\\n═══════════════════════════════════════════════════════════════');
            print('📌 TITLE: ' + article.title);
            print('═══════════════════════════════════════════════════════════════');
            print('\\n📋 METADATA:');
            print('  🏢 Company: ' + article.company);
            print('  📂 Factor Type: ' + article.factor_type);
            print('  📰 Publisher: ' + (article.publisher_name || 'N/A'));
            print('  ✍️  Author: ' + (article.author || 'N/A'));
            print('  🖼️  Icon: ' + (article.publisher_icon || 'N/A'));
            print('  📅 Published: ' + article.published_at);
            print('  📡 Source: ' + article.source);
            print('  🔗 Original URL: ' + (article.original_url || article.url));
            print('  🔗 Final URL: ' + article.url);
            print('\\n😊 SENTIMENT ANALYSIS:');
            print('  Label: ' + article.sentiment_label);
            print('  Score: ' + article.sentiment_score.toFixed(3));
            print('  Confidence: ' + article.sentiment_confidence);
            print('\\n💧 MARKET IMPACT:');
            print('  Liquidity Impact: ' + article.liquidity_impact);
            print('  Critical Events: ' + article.critical_events);
            print('  Investment Decisions: ' + article.decisions);
            print('\\n📝 CONTENT:');
            print('  Length: ' + article.content_length + ' characters');
            print('  Content Hash: ' + article.content_hash);
            if (article.summary) {
                print('\\n📄 LLM SUMMARY:');
                print('  ' + article.summary);
            }
            print('\\n🗂️  CLUSTERING:');
            print('  Cluster ID: ' + article.cluster_id);
            print('\\n📊 PROCESSING:');
            print('  Enriched At: ' + article.enriched_at);
            if (article.summarized_at) print('  Summarized At: ' + article.summarized_at);
            if (article.all_publishers && article.all_publishers.length > 0) {
                print('\\n📰 ALL PUBLISHERS (Deduplicated Sources):');
                article.all_publishers.forEach(pub => {
                    print('  • ' + pub.name + ' (' + pub.source + ')');
                    if (pub.icon) print('    Icon: ' + pub.icon);
                    print('    URL: ' + pub.url);
                });
            }
            print('\\n─── CONTENT PREVIEW ───');
            print(article.content.substring(0, 500) + '...');
            print('═══════════════════════════════════════════════════════════════');
        } else {
            print('❌ Article not found');
        }
        "
        ;;
    
    help|*)
        show_help
        ;;
esac
