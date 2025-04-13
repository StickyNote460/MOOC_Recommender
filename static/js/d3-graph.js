function drawDependencyGraph(graphData) {
    const width = 1200;
    const height = 600;

    // 清理画布
    d3.select("#graphCanvas").html("");

    const svg = d3.select("#graphCanvas")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    // 力导向图模拟
    const simulation = d3.forceSimulation()
        .force("link", d3.forceLink().id(d => d.id))
        .force("charge", d3.forceManyBody().strength(-800))
        .force("center", d3.forceCenter(width / 2, height / 2));

    // 绘制边
    const link = svg.append("g")
        .selectAll("line")
        .data(graphData.links)
        .enter().append("line")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6);

    // 绘制节点
    const node = svg.append("g")
        .selectAll("circle")
        .data(graphData.nodes)
        .enter().append("circle")
        .attr("r", 20)
        .attr("fill", d => d.is_target ? "#ff4d4f" : "#1890ff")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

    // 添加标签
    node.append("title")
        .text(d => d.name);

    // 动态更新
    simulation
        .nodes(graphData.nodes)
        .on("tick", () => {
            link.attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node.attr("cx", d => d.x)
                .attr("cy", d => d.y);
        });

    simulation.force("link")
        .links(graphData.links);

    // 拖动交互
    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }

    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }

    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }
}