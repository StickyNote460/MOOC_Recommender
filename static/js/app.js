// 课程搜索功能
// static/js/app.js
function searchCourse() {
    const courseInput = document.getElementById('courseInput').value;

    fetch(`/api/recommend/?course=${encodeURIComponent(courseInput)}`)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP 错误: ${response.status}`);
            return response.json();
        })
        .then(data => {
            const resultDiv = document.getElementById('pathResult');

            if (data.error) {
                // 显示错误消息
                resultDiv.innerHTML = `<div class="error-msg">${data.error}</div>`;
                return;
            }

            // static/js/app.js
            if (data.is_valid) {
                const preCourses = data.pre_courses || [];
                const targetName = data.target || '未知课程';
                // 直接生成 {A，B}→目标课程 格式
                const pathStr = `{${preCourses.join('，')}}→${targetName}`;
                resultDiv.innerHTML = pathStr;
                } else {
                // 显示无效推荐信息
                resultDiv.innerHTML = data.error_msg || '无推荐路径';
            }

            // 渲染知识图谱
            drawDependencyGraph(data.graph_data);
        })
        .catch(error => {
            console.error("请求失败:", error);
            document.getElementById('pathResult').innerHTML = "⚠️ 获取推荐失败，请稍后重试。";
        });
}// 显示推荐结果
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