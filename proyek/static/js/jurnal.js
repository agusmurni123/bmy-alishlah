const jurnal = document.querySelector('.dialog-jurnal');
    const addJurnal = document.getElementById('jurnal');
    const closeJurnal = document.getElementById('close-jurnal');
    addJurnal.addEventListener('click', function(){
        jurnal.style.display='block';
    });

    closeJurnal.addEventListener('click', function(){
        jurnal.style.display='none';
    });