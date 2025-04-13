function drawDependencyGraph(graphData) {
    const width = 1200;
    const height = 600;
    const container = d3.select("#graphCanvas");

    // 清空画布
    container.html("");

    // 空数据提示
    if (!graphData ||
        !graphData.nodes ||
        !graphData.links ||
        graphData.nodes.length === 0) {

        container.append("div")
            .style("text-align", "center")
            .style("padding", "20px")
            .html("<h4>📭 暂无课程依赖关系数据</h4>");
        return;  // 直接返回不执行后续绘图逻辑
    }

    // ---------- 以下是原有绘图逻辑 ----------
    const svg = container.append("svg")
        .attr("width", width)
        .attr("height", height);

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

    // 绘制节点（带颜色区分）
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

    // 节点文字标签
    const labels = svg.append("g")
        .selectAll("text")
        .data(graphData.nodes)
        .enter().append("text")
        .text(d => d.name)
        .attr("font-size", 12)
        .attr("dx", 25)
        .attr("dy", 5);

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

            labels.attr("x", d => d.x)
                  .attr("y", d => d.y);
        });

    simulation.force("link")
        .links(graphData.links);

    // 拖动交互函数
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