#!/usr/bin/env python3
"""Generate dashboard.html with embedded FIFA data and visualizations."""

import csv
import json
from pathlib import Path

def read_csv_to_json(filepath):
    """Read CSV file and return as list of dicts."""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def main():
    base_path = Path(__file__).parent / 'Dataset'

    # Read all datasets
    print("Reading datasets...")
    results = read_csv_to_json(base_path / 'results.csv')
    goalscorers = read_csv_to_json(base_path / 'goalscorers.csv')
    shootouts = read_csv_to_json(base_path / 'shootouts.csv')
    former_names = read_csv_to_json(base_path / 'former_names.csv')

    print(f"Loaded: {len(results)} results, {len(goalscorers)} goals, {len(shootouts)} shootouts")

    # Convert to JSON strings for embedding
    results_json = json.dumps(results)
    goalscorers_json = json.dumps(goalscorers)
    shootouts_json = json.dumps(shootouts)
    former_names_json = json.dumps(former_names)

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FIFA International Football Analytics</title>

    <!-- Google Fonts fallback for Berkeley Mono -->
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">

    <!-- D3.js -->
    <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
    <!-- Observable Plot -->
    <script src="https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6"></script>

    <style>
        :root {{
            --font-family: 'Berkeley Mono', 'JetBrains Mono', monospace;
            --bg-main: #10100E;
            --bg-main-rgb: 16, 16, 14;
            --bg-elevated: #1A1A18;
            --bg-elevated-rgb: 26, 26, 24;
            --bg-accent: #242422;
            --bg-accent-rgb: 36, 36, 34;
            --text-primary: #FFFFE3;
            --text-primary-rgb: 255, 255, 227;
            --text-secondary: #E6E6CE;
            --text-secondary-rgb: 230, 230, 206;
            --text-tertiary: #B3B3A3;
            --text-tertiary-rgb: 179, 179, 163;
            --lime: #BEFF00;
            --lime-rgb: 190, 255, 0;
            --cyan: #00BAFE;
            --cyan-rgb: 0, 186, 254;
            --amber: #FFC000;
            --amber-rgb: 255, 192, 0;
            --emerald: #00DE71;
            --emerald-rgb: 0, 222, 113;
            --coral: #F04E50;
            --coral-rgb: 240, 78, 80;
            --border: #2A2A28;
            --border-rgb: 42, 42, 40;
            --border-light: #3A3A38;
            --border-light-rgb: 58, 58, 56;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: var(--font-family);
            background: var(--bg-main);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 2rem;
        }}

        header {{
            text-align: center;
            padding: 3rem 0;
            border-bottom: 1px solid var(--border);
            margin-bottom: 2rem;
        }}

        h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--lime);
            margin-bottom: 0.5rem;
        }}

        .subtitle {{
            color: var(--text-secondary);
            font-size: 1rem;
        }}

        .stats-bar {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}

        .stat-card {{
            background: var(--bg-elevated);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }}

        .stat-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--cyan);
        }}

        .stat-label {{
            font-size: 0.75rem;
            color: var(--text-tertiary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .nav-tabs {{
            display: flex;
            gap: 0.5rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }}

        .tab-btn {{
            background: var(--bg-elevated);
            border: 1px solid var(--border);
            color: var(--text-secondary);
            padding: 0.75rem 1.25rem;
            border-radius: 6px;
            cursor: pointer;
            font-family: var(--font-family);
            font-size: 0.875rem;
            transition: all 0.2s ease;
        }}

        .tab-btn:hover {{
            border-color: var(--lime);
            color: var(--text-primary);
        }}

        .tab-btn.active {{
            background: var(--lime);
            color: var(--bg-main);
            border-color: var(--lime);
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 1.5rem;
        }}

        .chart-card {{
            background: var(--bg-elevated);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            overflow: hidden;
        }}

        .chart-card.full-width {{
            grid-column: 1 / -1;
        }}

        .chart-title {{
            font-size: 1rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
        }}

        .chart-description {{
            font-size: 0.75rem;
            color: var(--text-tertiary);
            margin-bottom: 1rem;
        }}

        .chart-container {{
            min-height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .chart-container svg {{
            max-width: 100%;
            height: auto;
        }}

        /* D3 chart styling */
        .axis text {{
            fill: var(--text-tertiary);
            font-family: var(--font-family);
            font-size: 10px;
        }}

        .axis line,
        .axis path {{
            stroke: var(--border);
        }}

        .grid line {{
            stroke: var(--border);
            stroke-opacity: 0.3;
        }}

        .tooltip {{
            position: absolute;
            background: var(--bg-accent);
            border: 1px solid var(--border-light);
            border-radius: 6px;
            padding: 0.75rem;
            font-size: 0.75rem;
            color: var(--text-primary);
            pointer-events: none;
            z-index: 1000;
            max-width: 250px;
        }}

        .loading {{
            color: var(--text-tertiary);
            font-style: italic;
        }}

        footer {{
            text-align: center;
            padding: 2rem 0;
            margin-top: 3rem;
            border-top: 1px solid var(--border);
            color: var(--text-tertiary);
            font-size: 0.75rem;
        }}

        footer a {{
            color: var(--cyan);
            text-decoration: none;
        }}

        footer a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>FIFA International Football Analytics</h1>
            <p class="subtitle">153 years of international football data (1872-2025)</p>
        </header>

        <div class="stats-bar" id="stats-bar">
            <div class="stat-card">
                <div class="stat-value" id="stat-matches">-</div>
                <div class="stat-label">Matches</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-goals">-</div>
                <div class="stat-label">Goals</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-teams">-</div>
                <div class="stat-label">Teams</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-scorers">-</div>
                <div class="stat-label">Scorers</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-tournaments">-</div>
                <div class="stat-label">Tournaments</div>
            </div>
        </div>

        <nav class="nav-tabs">
            <button class="tab-btn active" data-tab="temporal">Temporal</button>
            <button class="tab-btn" data-tab="network">Network</button>
            <button class="tab-btn" data-tab="distribution">Distribution</button>
            <button class="tab-btn" data-tab="comparative">Comparative</button>
            <button class="tab-btn" data-tab="statistical">Statistical</button>
        </nav>

        <!-- Temporal Analysis -->
        <div class="tab-content active" id="temporal">
            <div class="chart-grid">
                <div class="chart-card full-width">
                    <h3 class="chart-title">Goals Per Year (Streamgraph)</h3>
                    <p class="chart-description">Evolution of goal scoring across decades by tournament type</p>
                    <div class="chart-container" id="chart-streamgraph"></div>
                </div>
                <div class="chart-card">
                    <h3 class="chart-title">Match Frequency Heatmap</h3>
                    <p class="chart-description">Matches by month and day of week</p>
                    <div class="chart-container" id="chart-calendar"></div>
                </div>
                <div class="chart-card">
                    <h3 class="chart-title">Goals Per Match Over Time</h3>
                    <p class="chart-description">Average scoring trends across eras</p>
                    <div class="chart-container" id="chart-scoring-trend"></div>
                </div>
                <div class="chart-card">
                    <h3 class="chart-title">Home vs Away Goals</h3>
                    <p class="chart-description">Evolution of home advantage</p>
                    <div class="chart-container" id="chart-home-away"></div>
                </div>
                <div class="chart-card">
                    <h3 class="chart-title">Monthly Goal Distribution</h3>
                    <p class="chart-description">When do most goals get scored?</p>
                    <div class="chart-container" id="chart-monthly"></div>
                </div>
            </div>
        </div>

        <!-- Network Analysis -->
        <div class="tab-content" id="network">
            <div class="chart-grid">
                <div class="chart-card full-width">
                    <h3 class="chart-title">Team Matchup Matrix</h3>
                    <p class="chart-description">Frequency of matches between top teams</p>
                    <div class="chart-container" id="chart-matrix"></div>
                </div>
                <div class="chart-card">
                    <h3 class="chart-title">Tournament Distribution</h3>
                    <p class="chart-description">Breakdown of match types</p>
                    <div class="chart-container" id="chart-tournament-dist"></div>
                </div>
                <div class="chart-card">
                    <h3 class="chart-title">Neutral Venue Analysis</h3>
                    <p class="chart-description">Matches played on neutral ground</p>
                    <div class="chart-container" id="chart-neutral"></div>
                </div>
            </div>
        </div>

        <!-- Distribution Analysis -->
        <div class="tab-content" id="distribution">
            <div class="chart-grid">
                <div class="chart-card">
                    <h3 class="chart-title">Score Distribution</h3>
                    <p class="chart-description">Most common match results</p>
                    <div class="chart-container" id="chart-score-dist"></div>
                </div>
                <div class="chart-card">
                    <h3 class="chart-title">Goal Minute Distribution</h3>
                    <p class="chart-description">When goals are scored during matches</p>
                    <div class="chart-container" id="chart-minute"></div>
                </div>
                <div class="chart-card">
                    <h3 class="chart-title">Goal Types</h3>
                    <p class="chart-description">Regular vs Penalty vs Own Goals</p>
                    <div class="chart-container" id="chart-goal-types"></div>
                </div>
                <div class="chart-card">
                    <h3 class="chart-title">Top Scorers</h3>
                    <p class="chart-description">All-time leading goal scorers</p>
                    <div class="chart-container" id="chart-top-scorers"></div>
                </div>
            </div>
        </div>

        <!-- Comparative Analysis -->
        <div class="tab-content" id="comparative">
            <div class="chart-grid">
                <div class="chart-card full-width">
                    <h3 class="chart-title">Top Teams by Wins</h3>
                    <p class="chart-description">Most successful international teams</p>
                    <div class="chart-container" id="chart-top-teams"></div>
                </div>
                <div class="chart-card">
                    <h3 class="chart-title">Win Rate Comparison</h3>
                    <p class="chart-description">Home vs Away performance</p>
                    <div class="chart-container" id="chart-win-rate"></div>
                </div>
                <div class="chart-card">
                    <h3 class="chart-title">Goals Scored vs Conceded</h3>
                    <p class="chart-description">Offensive vs Defensive balance</p>
                    <div class="chart-container" id="chart-goals-balance"></div>
                </div>
            </div>
        </div>

        <!-- Statistical Analysis -->
        <div class="tab-content" id="statistical">
            <div class="chart-grid">
                <div class="chart-card">
                    <h3 class="chart-title">Score Correlation</h3>
                    <p class="chart-description">Home score vs Away score hexbin</p>
                    <div class="chart-container" id="chart-hexbin"></div>
                </div>
                <div class="chart-card">
                    <h3 class="chart-title">Penalty Shootout Trends</h3>
                    <p class="chart-description">Shootouts over time</p>
                    <div class="chart-container" id="chart-shootouts"></div>
                </div>
                <div class="chart-card full-width">
                    <h3 class="chart-title">Decade Comparison</h3>
                    <p class="chart-description">How football has changed by decade</p>
                    <div class="chart-container" id="chart-decades"></div>
                </div>
            </div>
        </div>

        <footer>
            <p>Data source: International Football Results from 1872 to 2025</p>
            <p>Built with D3.js and Observable Plot</p>
        </footer>
    </div>

    <!-- Tooltip -->
    <div class="tooltip" id="tooltip" style="display: none;"></div>

    <script>
        // Embedded data
        const resultsData = {results_json};
        const goalscorersData = {goalscorers_json};
        const shootoutsData = {shootouts_json};
        const formerNamesData = {former_names_json};

        // Color palette based on theme
        const colors = {{
            lime: '#BEFF00',
            cyan: '#00BAFE',
            amber: '#FFC000',
            emerald: '#00DE71',
            coral: '#F04E50',
            text: '#FFFFE3',
            textSecondary: '#E6E6CE',
            textTertiary: '#B3B3A3',
            bg: '#10100E',
            bgElevated: '#1A1A18',
            border: '#2A2A28'
        }};

        const colorScale = [colors.lime, colors.cyan, colors.amber, colors.emerald, colors.coral];

        // Parse dates and numbers
        resultsData.forEach(d => {{
            d.date = new Date(d.date);
            d.home_score = +d.home_score;
            d.away_score = +d.away_score;
            d.year = d.date.getFullYear();
            d.month = d.date.getMonth();
            d.decade = Math.floor(d.year / 10) * 10;
            d.total_goals = d.home_score + d.away_score;
        }});

        goalscorersData.forEach(d => {{
            d.date = new Date(d.date);
            d.minute = +d.minute || null;
            d.own_goal = d.own_goal === 'True' || d.own_goal === true;
            d.penalty = d.penalty === 'True' || d.penalty === true;
            d.year = d.date.getFullYear();
        }});

        shootoutsData.forEach(d => {{
            d.date = new Date(d.date);
            d.year = d.date.getFullYear();
        }});

        // Calculate statistics
        const uniqueTeams = new Set([...resultsData.map(d => d.home_team), ...resultsData.map(d => d.away_team)]);
        const uniqueScorers = new Set(goalscorersData.map(d => d.scorer));
        const uniqueTournaments = new Set(resultsData.map(d => d.tournament));

        // Update stats bar
        document.getElementById('stat-matches').textContent = resultsData.length.toLocaleString();
        document.getElementById('stat-goals').textContent = goalscorersData.length.toLocaleString();
        document.getElementById('stat-teams').textContent = uniqueTeams.size.toLocaleString();
        document.getElementById('stat-scorers').textContent = uniqueScorers.size.toLocaleString();
        document.getElementById('stat-tournaments').textContent = uniqueTournaments.size.toLocaleString();

        // Tab navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                btn.classList.add('active');
                document.getElementById(btn.dataset.tab).classList.add('active');
            }});
        }});

        // Tooltip helper
        const tooltip = d3.select('#tooltip');

        function showTooltip(event, html) {{
            tooltip
                .style('display', 'block')
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 10) + 'px')
                .html(html);
        }}

        function hideTooltip() {{
            tooltip.style('display', 'none');
        }}

        // Chart 1: Goals per year area chart
        function renderStreamgraph() {{
            const container = d3.select('#chart-streamgraph');
            const width = container.node().clientWidth || 800;
            const height = 350;
            const margin = {{top: 20, right: 30, bottom: 40, left: 50}};

            // Aggregate goals by year
            const goalsByYear = d3.rollup(resultsData,
                v => d3.sum(v, d => d.total_goals),
                d => d.year
            );

            const data = Array.from(goalsByYear, ([year, goals]) => ({{year, goals}}))
                .filter(d => d.year >= 1900)
                .sort((a, b) => a.year - b.year);

            const svg = container.append('svg')
                .attr('width', width)
                .attr('height', height);

            const x = d3.scaleLinear()
                .domain(d3.extent(data, d => d.year))
                .range([margin.left, width - margin.right]);

            const y = d3.scaleLinear()
                .domain([0, d3.max(data, d => d.goals)])
                .range([height - margin.bottom, margin.top]);

            const area = d3.area()
                .x(d => x(d.year))
                .y0(y(0))
                .y1(d => y(d.goals))
                .curve(d3.curveMonotoneX);

            // Gradient
            const gradient = svg.append('defs')
                .append('linearGradient')
                .attr('id', 'area-gradient')
                .attr('x1', '0%').attr('y1', '0%')
                .attr('x2', '0%').attr('y2', '100%');

            gradient.append('stop')
                .attr('offset', '0%')
                .attr('stop-color', colors.lime)
                .attr('stop-opacity', 0.8);

            gradient.append('stop')
                .attr('offset', '100%')
                .attr('stop-color', colors.lime)
                .attr('stop-opacity', 0.1);

            svg.append('path')
                .datum(data)
                .attr('fill', 'url(#area-gradient)')
                .attr('d', area);

            svg.append('path')
                .datum(data)
                .attr('fill', 'none')
                .attr('stroke', colors.lime)
                .attr('stroke-width', 2)
                .attr('d', d3.line()
                    .x(d => x(d.year))
                    .y(d => y(d.goals))
                    .curve(d3.curveMonotoneX));

            // Axes
            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(0,${{height - margin.bottom}})`)
                .call(d3.axisBottom(x).tickFormat(d3.format('d')));

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(${{margin.left}},0)`)
                .call(d3.axisLeft(y).ticks(5));
        }}

        // Chart 2: Calendar heatmap
        function renderCalendarHeatmap() {{
            const container = d3.select('#chart-calendar');
            const width = container.node().clientWidth || 400;
            const height = 250;
            const margin = {{top: 30, right: 20, bottom: 30, left: 60}};

            const matchesByDayMonth = d3.rollup(resultsData,
                v => v.length,
                d => d.date.getDay(),
                d => d.date.getMonth()
            );

            const data = [];
            for (let day = 0; day < 7; day++) {{
                for (let month = 0; month < 12; month++) {{
                    const count = matchesByDayMonth.get(day)?.get(month) || 0;
                    data.push({{day, month, count}});
                }}
            }}

            const svg = container.append('svg')
                .attr('width', width)
                .attr('height', height);

            const cellWidth = (width - margin.left - margin.right) / 12;
            const cellHeight = (height - margin.top - margin.bottom) / 7;

            const colorScale = d3.scaleSequential(d3.interpolate(colors.bgElevated, colors.cyan))
                .domain([0, d3.max(data, d => d.count)]);

            const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
            const months = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'];

            const cells = svg.selectAll('rect')
                .data(data)
                .enter()
                .append('rect')
                .attr('x', d => margin.left + d.month * cellWidth)
                .attr('y', d => margin.top + d.day * cellHeight)
                .attr('width', cellWidth - 2)
                .attr('height', cellHeight - 2)
                .attr('fill', d => colorScale(d.count))
                .attr('rx', 2)
                .on('mouseover', (event, d) => {{
                    showTooltip(event, `${{days[d.day]}}, ${{months[d.month]}}: ${{d.count.toLocaleString()}} matches`);
                }})
                .on('mouseout', hideTooltip);

            // Labels
            svg.selectAll('.day-label')
                .data(days)
                .enter()
                .append('text')
                .attr('class', 'axis')
                .attr('x', margin.left - 5)
                .attr('y', (d, i) => margin.top + i * cellHeight + cellHeight / 2)
                .attr('text-anchor', 'end')
                .attr('dominant-baseline', 'middle')
                .style('font-size', '9px')
                .text(d => d);

            svg.selectAll('.month-label')
                .data(months)
                .enter()
                .append('text')
                .attr('class', 'axis')
                .attr('x', (d, i) => margin.left + i * cellWidth + cellWidth / 2)
                .attr('y', margin.top - 10)
                .attr('text-anchor', 'middle')
                .style('font-size', '9px')
                .text(d => d);
        }}

        // Chart 3: Scoring trend
        function renderScoringTrend() {{
            const container = d3.select('#chart-scoring-trend');
            const width = container.node().clientWidth || 400;
            const height = 250;
            const margin = {{top: 20, right: 30, bottom: 40, left: 50}};

            const avgByYear = d3.rollup(resultsData,
                v => d3.mean(v, d => d.total_goals),
                d => d.year
            );

            const data = Array.from(avgByYear, ([year, avg]) => ({{year, avg}}))
                .filter(d => d.year >= 1900)
                .sort((a, b) => a.year - b.year);

            const svg = container.append('svg')
                .attr('width', width)
                .attr('height', height);

            const x = d3.scaleLinear()
                .domain(d3.extent(data, d => d.year))
                .range([margin.left, width - margin.right]);

            const y = d3.scaleLinear()
                .domain([0, d3.max(data, d => d.avg) * 1.1])
                .range([height - margin.bottom, margin.top]);

            svg.append('path')
                .datum(data)
                .attr('fill', 'none')
                .attr('stroke', colors.amber)
                .attr('stroke-width', 2)
                .attr('d', d3.line()
                    .x(d => x(d.year))
                    .y(d => y(d.avg))
                    .curve(d3.curveMonotoneX));

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(0,${{height - margin.bottom}})`)
                .call(d3.axisBottom(x).tickFormat(d3.format('d')));

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(${{margin.left}},0)`)
                .call(d3.axisLeft(y).ticks(5));
        }}

        // Chart 4: Home vs Away
        function renderHomeAway() {{
            const container = d3.select('#chart-home-away');
            const width = container.node().clientWidth || 400;
            const height = 250;
            const margin = {{top: 20, right: 30, bottom: 40, left: 50}};

            const byDecade = d3.rollup(resultsData.filter(d => d.decade >= 1900),
                v => ({{
                    home: d3.mean(v, d => d.home_score),
                    away: d3.mean(v, d => d.away_score)
                }}),
                d => d.decade
            );

            const data = Array.from(byDecade, ([decade, scores]) => ({{decade, ...scores}}))
                .sort((a, b) => a.decade - b.decade);

            const svg = container.append('svg')
                .attr('width', width)
                .attr('height', height);

            const x = d3.scaleBand()
                .domain(data.map(d => d.decade))
                .range([margin.left, width - margin.right])
                .padding(0.3);

            const y = d3.scaleLinear()
                .domain([0, d3.max(data, d => Math.max(d.home, d.away)) * 1.2])
                .range([height - margin.bottom, margin.top]);

            // Home bars
            svg.selectAll('.bar-home')
                .data(data)
                .enter()
                .append('rect')
                .attr('x', d => x(d.decade))
                .attr('y', d => y(d.home))
                .attr('width', x.bandwidth() / 2 - 2)
                .attr('height', d => y(0) - y(d.home))
                .attr('fill', colors.emerald);

            // Away bars
            svg.selectAll('.bar-away')
                .data(data)
                .enter()
                .append('rect')
                .attr('x', d => x(d.decade) + x.bandwidth() / 2)
                .attr('y', d => y(d.away))
                .attr('width', x.bandwidth() / 2 - 2)
                .attr('height', d => y(0) - y(d.away))
                .attr('fill', colors.coral);

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(0,${{height - margin.bottom}})`)
                .call(d3.axisBottom(x).tickFormat(d => d + 's'));

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(${{margin.left}},0)`)
                .call(d3.axisLeft(y).ticks(5));
        }}

        // Chart 5: Monthly distribution
        function renderMonthly() {{
            const container = d3.select('#chart-monthly');
            const width = container.node().clientWidth || 400;
            const height = 250;
            const margin = {{top: 20, right: 20, bottom: 40, left: 50}};

            const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            const goalsByMonth = d3.rollup(goalscorersData, v => v.length, d => d.date.getMonth());
            const data = months.map((name, i) => ({{name, goals: goalsByMonth.get(i) || 0}}));

            const svg = container.append('svg')
                .attr('width', width)
                .attr('height', height);

            const x = d3.scaleBand()
                .domain(months)
                .range([margin.left, width - margin.right])
                .padding(0.2);

            const y = d3.scaleLinear()
                .domain([0, d3.max(data, d => d.goals)])
                .range([height - margin.bottom, margin.top]);

            svg.selectAll('rect')
                .data(data)
                .enter()
                .append('rect')
                .attr('x', d => x(d.name))
                .attr('y', d => y(d.goals))
                .attr('width', x.bandwidth())
                .attr('height', d => y(0) - y(d.goals))
                .attr('fill', colors.cyan)
                .attr('rx', 3);

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(0,${{height - margin.bottom}})`)
                .call(d3.axisBottom(x));

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(${{margin.left}},0)`)
                .call(d3.axisLeft(y).ticks(5));
        }}

        // Chart 6: Tournament distribution (treemap)
        function renderTournamentDist() {{
            const container = d3.select('#chart-tournament-dist');
            const width = container.node().clientWidth || 400;
            const height = 300;

            const tournamentCounts = d3.rollup(resultsData, v => v.length, d => d.tournament);
            const data = Array.from(tournamentCounts, ([name, value]) => ({{name, value}}))
                .sort((a, b) => b.value - a.value)
                .slice(0, 10);

            const svg = container.append('svg')
                .attr('width', width)
                .attr('height', height);

            const root = d3.hierarchy({{children: data}})
                .sum(d => d.value);

            d3.treemap()
                .size([width, height])
                .padding(2)(root);

            const color = d3.scaleOrdinal()
                .domain(data.map(d => d.name))
                .range(colorScale);

            const nodes = svg.selectAll('g')
                .data(root.leaves())
                .enter()
                .append('g')
                .attr('transform', d => `translate(${{d.x0}},${{d.y0}})`);

            nodes.append('rect')
                .attr('width', d => d.x1 - d.x0)
                .attr('height', d => d.y1 - d.y0)
                .attr('fill', d => color(d.data.name))
                .attr('rx', 4)
                .on('mouseover', (event, d) => {{
                    showTooltip(event, `<strong>${{d.data.name}}</strong><br>${{d.data.value.toLocaleString()}} matches`);
                }})
                .on('mouseout', hideTooltip);

            nodes.append('text')
                .attr('x', 5)
                .attr('y', 15)
                .text(d => {{
                    const width = d.x1 - d.x0;
                    if (width < 60) return '';
                    return d.data.name.length > 15 ? d.data.name.slice(0, 12) + '...' : d.data.name;
                }})
                .attr('fill', colors.bg)
                .style('font-size', '10px')
                .style('font-weight', '600');
        }}

        // Chart 7: Neutral venues
        function renderNeutral() {{
            const container = d3.select('#chart-neutral');
            const width = container.node().clientWidth || 400;
            const height = 250;

            const neutral = resultsData.filter(d => d.neutral === 'True' || d.neutral === true).length;
            const nonNeutral = resultsData.length - neutral;

            const data = [
                {{label: 'Regular', value: nonNeutral, color: colors.cyan}},
                {{label: 'Neutral', value: neutral, color: colors.amber}}
            ];

            const svg = container.append('svg')
                .attr('width', width)
                .attr('height', height);

            const radius = Math.min(width, height) / 2 - 40;
            const g = svg.append('g')
                .attr('transform', `translate(${{width/2}},${{height/2}})`);

            const pie = d3.pie().value(d => d.value);
            const arc = d3.arc().innerRadius(radius * 0.6).outerRadius(radius);

            g.selectAll('path')
                .data(pie(data))
                .enter()
                .append('path')
                .attr('d', arc)
                .attr('fill', d => d.data.color)
                .on('mouseover', (event, d) => {{
                    showTooltip(event, `<strong>${{d.data.label}}</strong><br>${{d.data.value.toLocaleString()}} matches (${{(d.data.value / resultsData.length * 100).toFixed(1)}}%)`);
                }})
                .on('mouseout', hideTooltip);

            // Center text
            g.append('text')
                .attr('text-anchor', 'middle')
                .attr('dy', '-0.5em')
                .style('fill', colors.text)
                .style('font-size', '12px')
                .text('Venue');

            g.append('text')
                .attr('text-anchor', 'middle')
                .attr('dy', '1em')
                .style('fill', colors.textTertiary)
                .style('font-size', '10px')
                .text('Type');
        }}

        // Chart 8: Score distribution
        function renderScoreDist() {{
            const container = d3.select('#chart-score-dist');
            const width = container.node().clientWidth || 400;
            const height = 250;
            const margin = {{top: 20, right: 20, bottom: 40, left: 60}};

            const scoreCounts = d3.rollup(resultsData,
                v => v.length,
                d => `${{d.home_score}}-${{d.away_score}}`
            );

            const data = Array.from(scoreCounts, ([score, count]) => ({{score, count}}))
                .sort((a, b) => b.count - a.count)
                .slice(0, 15);

            const svg = container.append('svg')
                .attr('width', width)
                .attr('height', height);

            const x = d3.scaleLinear()
                .domain([0, d3.max(data, d => d.count)])
                .range([margin.left, width - margin.right]);

            const y = d3.scaleBand()
                .domain(data.map(d => d.score))
                .range([margin.top, height - margin.bottom])
                .padding(0.2);

            svg.selectAll('rect')
                .data(data)
                .enter()
                .append('rect')
                .attr('x', margin.left)
                .attr('y', d => y(d.score))
                .attr('width', d => x(d.count) - margin.left)
                .attr('height', y.bandwidth())
                .attr('fill', colors.lime)
                .attr('rx', 3);

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(0,${{height - margin.bottom}})`)
                .call(d3.axisBottom(x).ticks(5));

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(${{margin.left}},0)`)
                .call(d3.axisLeft(y));
        }}

        // Chart 9: Goal minute distribution
        function renderMinute() {{
            const container = d3.select('#chart-minute');
            const width = container.node().clientWidth || 400;
            const height = 250;
            const margin = {{top: 20, right: 20, bottom: 40, left: 50}};

            const minuteData = goalscorersData.filter(d => d.minute && d.minute > 0 && d.minute <= 120);
            const byMinute = d3.rollup(minuteData, v => v.length, d => Math.floor(d.minute / 5) * 5);

            const data = Array.from(byMinute, ([minute, count]) => ({{minute, count}}))
                .sort((a, b) => a.minute - b.minute);

            const svg = container.append('svg')
                .attr('width', width)
                .attr('height', height);

            const x = d3.scaleLinear()
                .domain([0, 120])
                .range([margin.left, width - margin.right]);

            const y = d3.scaleLinear()
                .domain([0, d3.max(data, d => d.count)])
                .range([height - margin.bottom, margin.top]);

            svg.selectAll('rect')
                .data(data)
                .enter()
                .append('rect')
                .attr('x', d => x(d.minute))
                .attr('y', d => y(d.count))
                .attr('width', (width - margin.left - margin.right) / 24 - 1)
                .attr('height', d => y(0) - y(d.count))
                .attr('fill', colors.emerald);

            // Half-time marker
            svg.append('line')
                .attr('x1', x(45))
                .attr('x2', x(45))
                .attr('y1', margin.top)
                .attr('y2', height - margin.bottom)
                .attr('stroke', colors.coral)
                .attr('stroke-dasharray', '4');

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(0,${{height - margin.bottom}})`)
                .call(d3.axisBottom(x).ticks(10));

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(${{margin.left}},0)`)
                .call(d3.axisLeft(y).ticks(5));
        }}

        // Chart 10: Goal types
        function renderGoalTypes() {{
            const container = d3.select('#chart-goal-types');
            const width = container.node().clientWidth || 400;
            const height = 250;

            const penalties = goalscorersData.filter(d => d.penalty).length;
            const ownGoals = goalscorersData.filter(d => d.own_goal).length;
            const regular = goalscorersData.length - penalties - ownGoals;

            const data = [
                {{label: 'Regular', value: regular, color: colors.lime}},
                {{label: 'Penalty', value: penalties, color: colors.amber}},
                {{label: 'Own Goal', value: ownGoals, color: colors.coral}}
            ];

            const svg = container.append('svg')
                .attr('width', width)
                .attr('height', height);

            const radius = Math.min(width, height) / 2 - 40;
            const g = svg.append('g')
                .attr('transform', `translate(${{width/2}},${{height/2}})`);

            const pie = d3.pie().value(d => d.value);
            const arc = d3.arc().innerRadius(0).outerRadius(radius);

            g.selectAll('path')
                .data(pie(data))
                .enter()
                .append('path')
                .attr('d', arc)
                .attr('fill', d => d.data.color)
                .on('mouseover', (event, d) => {{
                    showTooltip(event, `<strong>${{d.data.label}}</strong><br>${{d.data.value.toLocaleString()}} goals (${{(d.data.value / goalscorersData.length * 100).toFixed(1)}}%)`);
                }})
                .on('mouseout', hideTooltip);
        }}

        // Chart 11: Top scorers
        function renderTopScorers() {{
            const container = d3.select('#chart-top-scorers');
            const width = container.node().clientWidth || 400;
            const height = 300;
            const margin = {{top: 20, right: 20, bottom: 20, left: 120}};

            const scorerCounts = d3.rollup(goalscorersData, v => v.length, d => d.scorer);
            const data = Array.from(scorerCounts, ([scorer, goals]) => ({{scorer, goals}}))
                .sort((a, b) => b.goals - a.goals)
                .slice(0, 15);

            const svg = container.append('svg')
                .attr('width', width)
                .attr('height', height);

            const x = d3.scaleLinear()
                .domain([0, d3.max(data, d => d.goals)])
                .range([margin.left, width - margin.right]);

            const y = d3.scaleBand()
                .domain(data.map(d => d.scorer))
                .range([margin.top, height - margin.bottom])
                .padding(0.2);

            svg.selectAll('rect')
                .data(data)
                .enter()
                .append('rect')
                .attr('x', margin.left)
                .attr('y', d => y(d.scorer))
                .attr('width', d => x(d.goals) - margin.left)
                .attr('height', y.bandwidth())
                .attr('fill', colors.cyan)
                .attr('rx', 3);

            // Goal count labels
            svg.selectAll('.goal-label')
                .data(data)
                .enter()
                .append('text')
                .attr('x', d => x(d.goals) + 5)
                .attr('y', d => y(d.scorer) + y.bandwidth() / 2)
                .attr('dominant-baseline', 'middle')
                .style('fill', colors.textTertiary)
                .style('font-size', '9px')
                .text(d => d.goals);

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(${{margin.left}},0)`)
                .call(d3.axisLeft(y))
                .selectAll('text')
                .style('font-size', '9px');
        }}

        // Chart 12: Top teams
        function renderTopTeams() {{
            const container = d3.select('#chart-top-teams');
            const width = container.node().clientWidth || 800;
            const height = 300;
            const margin = {{top: 20, right: 20, bottom: 60, left: 50}};

            // Calculate wins per team
            const wins = new Map();
            resultsData.forEach(d => {{
                if (d.home_score > d.away_score) {{
                    wins.set(d.home_team, (wins.get(d.home_team) || 0) + 1);
                }} else if (d.away_score > d.home_score) {{
                    wins.set(d.away_team, (wins.get(d.away_team) || 0) + 1);
                }}
            }});

            const data = Array.from(wins, ([team, count]) => ({{team, wins: count}}))
                .sort((a, b) => b.wins - a.wins)
                .slice(0, 20);

            const svg = container.append('svg')
                .attr('width', width)
                .attr('height', height);

            const x = d3.scaleBand()
                .domain(data.map(d => d.team))
                .range([margin.left, width - margin.right])
                .padding(0.2);

            const y = d3.scaleLinear()
                .domain([0, d3.max(data, d => d.wins)])
                .range([height - margin.bottom, margin.top]);

            svg.selectAll('rect')
                .data(data)
                .enter()
                .append('rect')
                .attr('x', d => x(d.team))
                .attr('y', d => y(d.wins))
                .attr('width', x.bandwidth())
                .attr('height', d => y(0) - y(d.wins))
                .attr('fill', colors.lime)
                .attr('rx', 3)
                .on('mouseover', (event, d) => {{
                    showTooltip(event, `<strong>${{d.team}}</strong><br>${{d.wins.toLocaleString()}} wins`);
                }})
                .on('mouseout', hideTooltip);

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(0,${{height - margin.bottom}})`)
                .call(d3.axisBottom(x))
                .selectAll('text')
                .attr('transform', 'rotate(-45)')
                .style('text-anchor', 'end')
                .style('font-size', '9px');

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(${{margin.left}},0)`)
                .call(d3.axisLeft(y).ticks(5));
        }}

        // Chart 13: Win rate comparison
        function renderWinRate() {{
            const container = d3.select('#chart-win-rate');
            const width = container.node().clientWidth || 400;
            const height = 250;
            const margin = {{top: 20, right: 20, bottom: 60, left: 50}};

            // Calculate home/away wins by team
            const teamStats = new Map();
            resultsData.forEach(d => {{
                // Home team
                if (!teamStats.has(d.home_team)) {{
                    teamStats.set(d.home_team, {{homeWins: 0, homeGames: 0, awayWins: 0, awayGames: 0}});
                }}
                const home = teamStats.get(d.home_team);
                home.homeGames++;
                if (d.home_score > d.away_score) home.homeWins++;

                // Away team
                if (!teamStats.has(d.away_team)) {{
                    teamStats.set(d.away_team, {{homeWins: 0, homeGames: 0, awayWins: 0, awayGames: 0}});
                }}
                const away = teamStats.get(d.away_team);
                away.awayGames++;
                if (d.away_score > d.home_score) away.awayWins++;
            }});

            const data = Array.from(teamStats, ([team, stats]) => ({{
                team,
                homeRate: stats.homeGames > 50 ? stats.homeWins / stats.homeGames : null,
                awayRate: stats.awayGames > 50 ? stats.awayWins / stats.awayGames : null
            }}))
                .filter(d => d.homeRate !== null && d.awayRate !== null)
                .sort((a, b) => (b.homeRate + b.awayRate) - (a.homeRate + a.awayRate))
                .slice(0, 10);

            const svg = container.append('svg')
                .attr('width', width)
                .attr('height', height);

            const x = d3.scaleBand()
                .domain(data.map(d => d.team))
                .range([margin.left, width - margin.right])
                .padding(0.3);

            const y = d3.scaleLinear()
                .domain([0, 1])
                .range([height - margin.bottom, margin.top]);

            // Dumbbell chart
            data.forEach(d => {{
                const xPos = x(d.team) + x.bandwidth() / 2;

                // Line connecting dots
                svg.append('line')
                    .attr('x1', xPos)
                    .attr('x2', xPos)
                    .attr('y1', y(d.homeRate))
                    .attr('y2', y(d.awayRate))
                    .attr('stroke', colors.border)
                    .attr('stroke-width', 2);

                // Home dot
                svg.append('circle')
                    .attr('cx', xPos)
                    .attr('cy', y(d.homeRate))
                    .attr('r', 5)
                    .attr('fill', colors.emerald);

                // Away dot
                svg.append('circle')
                    .attr('cx', xPos)
                    .attr('cy', y(d.awayRate))
                    .attr('r', 5)
                    .attr('fill', colors.coral);
            }});

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(0,${{height - margin.bottom}})`)
                .call(d3.axisBottom(x))
                .selectAll('text')
                .attr('transform', 'rotate(-45)')
                .style('text-anchor', 'end')
                .style('font-size', '8px');

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(${{margin.left}},0)`)
                .call(d3.axisLeft(y).ticks(5).tickFormat(d => (d * 100) + '%'));
        }}

        // Chart 14: Goals balance scatter
        function renderGoalsBalance() {{
            const container = d3.select('#chart-goals-balance');
            const width = container.node().clientWidth || 400;
            const height = 250;
            const margin = {{top: 20, right: 20, bottom: 40, left: 50}};

            // Calculate goals scored/conceded per team
            const teamGoals = new Map();
            resultsData.forEach(d => {{
                if (!teamGoals.has(d.home_team)) {{
                    teamGoals.set(d.home_team, {{scored: 0, conceded: 0}});
                }}
                if (!teamGoals.has(d.away_team)) {{
                    teamGoals.set(d.away_team, {{scored: 0, conceded: 0}});
                }}
                teamGoals.get(d.home_team).scored += d.home_score;
                teamGoals.get(d.home_team).conceded += d.away_score;
                teamGoals.get(d.away_team).scored += d.away_score;
                teamGoals.get(d.away_team).conceded += d.home_score;
            }});

            const data = Array.from(teamGoals, ([team, goals]) => ({{team, ...goals}}))
                .filter(d => d.scored > 100)
                .sort((a, b) => (b.scored - b.conceded) - (a.scored - a.conceded))
                .slice(0, 50);

            const svg = container.append('svg')
                .attr('width', width)
                .attr('height', height);

            const maxGoals = d3.max(data, d => Math.max(d.scored, d.conceded));

            const x = d3.scaleLinear()
                .domain([0, maxGoals])
                .range([margin.left, width - margin.right]);

            const y = d3.scaleLinear()
                .domain([0, maxGoals])
                .range([height - margin.bottom, margin.top]);

            // Diagonal line (balance)
            svg.append('line')
                .attr('x1', x(0))
                .attr('y1', y(0))
                .attr('x2', x(maxGoals))
                .attr('y2', y(maxGoals))
                .attr('stroke', colors.border)
                .attr('stroke-dasharray', '4');

            svg.selectAll('circle')
                .data(data)
                .enter()
                .append('circle')
                .attr('cx', d => x(d.scored))
                .attr('cy', d => y(d.conceded))
                .attr('r', 4)
                .attr('fill', d => d.scored > d.conceded ? colors.emerald : colors.coral)
                .attr('opacity', 0.7)
                .on('mouseover', (event, d) => {{
                    showTooltip(event, `<strong>${{d.team}}</strong><br>Scored: ${{d.scored}}<br>Conceded: ${{d.conceded}}`);
                }})
                .on('mouseout', hideTooltip);

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(0,${{height - margin.bottom}})`)
                .call(d3.axisBottom(x).ticks(5));

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(${{margin.left}},0)`)
                .call(d3.axisLeft(y).ticks(5));

            // Labels
            svg.append('text')
                .attr('x', width / 2)
                .attr('y', height - 5)
                .attr('text-anchor', 'middle')
                .style('fill', colors.textTertiary)
                .style('font-size', '9px')
                .text('Goals Scored');

            svg.append('text')
                .attr('transform', 'rotate(-90)')
                .attr('x', -height / 2)
                .attr('y', 12)
                .attr('text-anchor', 'middle')
                .style('fill', colors.textTertiary)
                .style('font-size', '9px')
                .text('Goals Conceded');
        }}

        // Chart 15: Hexbin
        function renderHexbin() {{
            const container = d3.select('#chart-hexbin');
            const width = container.node().clientWidth || 400;
            const height = 250;
            const margin = {{top: 20, right: 20, bottom: 40, left: 50}};

            const svg = container.append('svg')
                .attr('width', width)
                .attr('height', height);

            const x = d3.scaleLinear()
                .domain([0, 10])
                .range([margin.left, width - margin.right]);

            const y = d3.scaleLinear()
                .domain([0, 10])
                .range([height - margin.bottom, margin.top]);

            // Count score combinations
            const scoreCounts = d3.rollup(resultsData,
                v => v.length,
                d => d.home_score,
                d => d.away_score
            );

            const data = [];
            scoreCounts.forEach((awayCounts, homeScore) => {{
                awayCounts.forEach((count, awayScore) => {{
                    if (homeScore <= 10 && awayScore <= 10) {{
                        data.push({{homeScore, awayScore, count}});
                    }}
                }});
            }});

            const maxCount = d3.max(data, d => d.count);
            const colorScale = d3.scaleSequential(d3.interpolate(colors.bgElevated, colors.lime))
                .domain([0, maxCount]);

            const cellSize = (width - margin.left - margin.right) / 11;

            svg.selectAll('rect')
                .data(data)
                .enter()
                .append('rect')
                .attr('x', d => x(d.homeScore) - cellSize / 2)
                .attr('y', d => y(d.awayScore) - cellSize / 2)
                .attr('width', cellSize - 1)
                .attr('height', cellSize - 1)
                .attr('fill', d => colorScale(d.count))
                .attr('rx', 2)
                .on('mouseover', (event, d) => {{
                    showTooltip(event, `${{d.homeScore}}-${{d.awayScore}}: ${{d.count.toLocaleString()}} matches`);
                }})
                .on('mouseout', hideTooltip);

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(0,${{height - margin.bottom}})`)
                .call(d3.axisBottom(x).ticks(10));

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(${{margin.left}},0)`)
                .call(d3.axisLeft(y).ticks(10));
        }}

        // Chart 16: Shootouts over time
        function renderShootouts() {{
            const container = d3.select('#chart-shootouts');
            const width = container.node().clientWidth || 400;
            const height = 250;
            const margin = {{top: 20, right: 20, bottom: 40, left: 50}};

            const byYear = d3.rollup(shootoutsData, v => v.length, d => d.year);
            const data = Array.from(byYear, ([year, count]) => ({{year, count}}))
                .sort((a, b) => a.year - b.year);

            const svg = container.append('svg')
                .attr('width', width)
                .attr('height', height);

            const x = d3.scaleLinear()
                .domain(d3.extent(data, d => d.year))
                .range([margin.left, width - margin.right]);

            const y = d3.scaleLinear()
                .domain([0, d3.max(data, d => d.count)])
                .range([height - margin.bottom, margin.top]);

            svg.selectAll('circle')
                .data(data)
                .enter()
                .append('circle')
                .attr('cx', d => x(d.year))
                .attr('cy', d => y(d.count))
                .attr('r', 3)
                .attr('fill', colors.coral);

            svg.append('path')
                .datum(data)
                .attr('fill', 'none')
                .attr('stroke', colors.coral)
                .attr('stroke-width', 1.5)
                .attr('d', d3.line()
                    .x(d => x(d.year))
                    .y(d => y(d.count))
                    .curve(d3.curveMonotoneX));

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(0,${{height - margin.bottom}})`)
                .call(d3.axisBottom(x).tickFormat(d3.format('d')));

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(${{margin.left}},0)`)
                .call(d3.axisLeft(y).ticks(5));
        }}

        // Chart 17: Decades comparison
        function renderDecades() {{
            const container = d3.select('#chart-decades');
            const width = container.node().clientWidth || 800;
            const height = 300;
            const margin = {{top: 30, right: 20, bottom: 40, left: 60}};

            const decadeStats = d3.rollup(resultsData.filter(d => d.decade >= 1900),
                v => ({{
                    matches: v.length,
                    avgGoals: d3.mean(v, d => d.total_goals),
                    homeWinPct: v.filter(d => d.home_score > d.away_score).length / v.length
                }}),
                d => d.decade
            );

            const data = Array.from(decadeStats, ([decade, stats]) => ({{decade, ...stats}}))
                .sort((a, b) => a.decade - b.decade);

            const svg = container.append('svg')
                .attr('width', width)
                .attr('height', height);

            const x = d3.scaleBand()
                .domain(data.map(d => d.decade))
                .range([margin.left, width - margin.right])
                .padding(0.2);

            const yLeft = d3.scaleLinear()
                .domain([0, d3.max(data, d => d.matches)])
                .range([height - margin.bottom, margin.top]);

            const yRight = d3.scaleLinear()
                .domain([0, d3.max(data, d => d.avgGoals) * 1.2])
                .range([height - margin.bottom, margin.top]);

            // Bars for matches
            svg.selectAll('.bar')
                .data(data)
                .enter()
                .append('rect')
                .attr('x', d => x(d.decade))
                .attr('y', d => yLeft(d.matches))
                .attr('width', x.bandwidth())
                .attr('height', d => yLeft(0) - yLeft(d.matches))
                .attr('fill', colors.cyan)
                .attr('opacity', 0.6);

            // Line for avg goals
            svg.append('path')
                .datum(data)
                .attr('fill', 'none')
                .attr('stroke', colors.amber)
                .attr('stroke-width', 3)
                .attr('d', d3.line()
                    .x(d => x(d.decade) + x.bandwidth() / 2)
                    .y(d => yRight(d.avgGoals)));

            svg.selectAll('.dot')
                .data(data)
                .enter()
                .append('circle')
                .attr('cx', d => x(d.decade) + x.bandwidth() / 2)
                .attr('cy', d => yRight(d.avgGoals))
                .attr('r', 4)
                .attr('fill', colors.amber);

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(0,${{height - margin.bottom}})`)
                .call(d3.axisBottom(x).tickFormat(d => d + 's'));

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(${{margin.left}},0)`)
                .call(d3.axisLeft(yLeft).ticks(5));

            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(${{width - margin.right}},0)`)
                .call(d3.axisRight(yRight).ticks(5));

            // Legend
            svg.append('rect')
                .attr('x', margin.left + 10)
                .attr('y', margin.top)
                .attr('width', 12)
                .attr('height', 12)
                .attr('fill', colors.cyan)
                .attr('opacity', 0.6);

            svg.append('text')
                .attr('x', margin.left + 28)
                .attr('y', margin.top + 10)
                .style('fill', colors.textSecondary)
                .style('font-size', '10px')
                .text('Matches');

            svg.append('circle')
                .attr('cx', margin.left + 100)
                .attr('cy', margin.top + 6)
                .attr('r', 5)
                .attr('fill', colors.amber);

            svg.append('text')
                .attr('x', margin.left + 112)
                .attr('y', margin.top + 10)
                .style('fill', colors.textSecondary)
                .style('font-size', '10px')
                .text('Avg Goals');
        }}

        // Render all charts
        renderStreamgraph();
        renderCalendarHeatmap();
        renderScoringTrend();
        renderHomeAway();
        renderMonthly();
        renderTournamentDist();
        renderNeutral();
        renderScoreDist();
        renderMinute();
        renderGoalTypes();
        renderTopScorers();
        renderTopTeams();
        renderWinRate();
        renderGoalsBalance();
        renderHexbin();
        renderShootouts();
        renderDecades();
    </script>
</body>
</html>'''

    # Write the HTML file
    output_path = Path(__file__).parent / 'dashboard.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Dashboard generated: {{output_path}}")
    print(f"File size: {{output_path.stat().st_size / 1024 / 1024:.2f}} MB")

if __name__ == '__main__':
    main()
