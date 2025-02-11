
    const addButton = document.getElementById('profil');
    const dialog = document.querySelector('.dialog-form');
    const closeAkun = document.getElementById('close-akun');

    addButton.addEventListener('click', function(){
        dialog.style.display='block';
    });
    
    closeAkun.addEventListener('click', function(){
        dialog.style.display='none';
    });


    // konversi pdf
    async function printPDF() {
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF('p', 'pt', 'a4');
        const pageHeight = pdf.internal.pageSize.getHeight();
        const element = document.querySelector('.payments');

        // Menggunakan html2canvas untuk mengkonversi elemen HTML menjadi canvas
        const canvas = await html2canvas(element);
        const imgData = canvas.toDataURL('image/png');

        // Mengambil dimensi canvas
        const imgWidth = canvas.width;
        const imgHeight = canvas.height;

        // Tinggi setiap bagian yang akan dimuat dalam satu halaman PDF
        const heightOfOnePart = (canvas.height / 120) * 25;

        let position = 0;

        for (let i = 0; i < Math.ceil(120 / 25); i++) {
            // Mendapatkan bagian dari canvas yang sesuai dengan halaman saat ini
            const sectionCanvas = document.createElement('canvas');
            sectionCanvas.width = canvas.width;
            sectionCanvas.height = heightOfOnePart;
            const context = sectionCanvas.getContext('2d');
            context.drawImage(canvas, 0, -position, canvas.width, canvas.height);

            const sectionImgData = sectionCanvas.toDataURL('image/png');
            if (i > 0) pdf.addPage();
            pdf.addImage(sectionImgData, 'PNG', 0, 0, pdf.internal.pageSize.getWidth(), pageHeight);

            position += heightOfOnePart;
        }

        pdf.save('donasi.pdf');
    }
