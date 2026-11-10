// 全站通用：删除前确认 + 文章页代码高亮。
document.addEventListener("submit", (event) => {
  const message = event.target.dataset.confirm;
  if (message && !window.confirm(message)) {
    event.preventDefault();
  }
});

if (window.hljs) {
  document.querySelectorAll(".content pre code").forEach((block) => {
    hljs.highlightElement(block);
  });
}
