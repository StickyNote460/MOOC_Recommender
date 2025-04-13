// 课程搜索功能
// static/js/app.js
function searchCourse() {
    const courseInput = document.getElementById('courseInput').value;
    console.log("请求课程:", courseInput);  // 调试日志

    fetch(`/api/recommend/?course=${encodeURIComponent(courseInput)}`)
        .then(response => {
            console.log("响应状态码:", response.status);  // 调试日志
            if (!response.ok) throw new Error(`HTTP 错误: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log("响应数据:", data);  // 调试日志
            if (data.path) {
                document.getElementById('pathResult').innerHTML = data.path.join(' → ');
                drawDependencyGraph(data.graph_data);
            } else {
                throw new Error("响应未包含 path 字段");
            }
        })
        .catch(error => {
            console.error("请求失败:", error);
            document.getElementById('pathResult').innerHTML = "⚠️ 获取推荐失败，请稍后重试。";
        });
}
// 显示推荐结果
function displayRecommendation(data) {
    const resultDiv = document.getElementById('pathResult')

    if (data.error) {
        resultDiv.innerHTML = `<div class="error-msg">${data.error}</div>`
        return
    }

    resultDiv.innerHTML = `
        <div class="path-display">
            <span class="path-badge">推荐路径</span>
            ${data.path || '暂无推荐路径'}
        </div>
        ${data.description ? `<p class="path-desc">${data.description}</p>` : ''}
    `
}

// 错误处理
function showError(msg) {
    const resultDiv = document.getElementById('pathResult')
    resultDiv.innerHTML = `<div class="error-msg">⚠️ ${msg}</div>`
}