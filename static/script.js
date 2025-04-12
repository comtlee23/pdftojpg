// 파일 위치: static/script.js

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("upload-form");
    const resultDiv = document.getElementById("result");
    const downloadLink = document.getElementById("download-link");

    form.addEventListener("submit", function (e) {
        e.preventDefault(); // 폼 기본 동작(새로고침) 방지

        const fileInput = document.getElementById("pdf-file");
        const file = fileInput.files[0];

        if (!file) {
            alert("PDF 파일을 선택해주세요.");
            return;
        }

        const formData = new FormData();
        formData.append("pdf_file", file);

        // 서버로 PDF 파일 전송
        fetch("/convert", {
            method: "POST",
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("서버 오류가 발생했습니다.");
            }
            return response.json();  // 서버에서 JSON 형태로 응답 기대
        })
        .then(data => {
            // 변환 성공 시 다운로드 링크 보여주기
            if (data.success && data.download_url) {
                downloadLink.href = data.download_url;
                resultDiv.style.display = "block";
            } else {
                alert("변환에 실패했습니다.");
            }
        })
        .catch(error => {
            console.error("에러:", error);
            alert("변환 중 오류가 발생했습니다.");
        });
    });
});
