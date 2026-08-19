document.addEventListener("DOMContentLoaded", function () {

    /*
     * =========================================================
     * DOM ELEMENTS
     * =========================================================
     */

    const audioPlayer =
        document.getElementById("audio-player");

    const playerTitle =
        document.getElementById("player-title");

    const playerArtist =
        document.getElementById("player-artist");

    const playerPlayButton =
        document.getElementById("player-play-button");

    const previousButton =
        document.getElementById("previous-button");

    const nextButton =
        document.getElementById("next-button");

    const progressBar =
        document.getElementById("progress-bar");

    const currentTimeElement =
        document.getElementById("current-time");

    const durationElement =
        document.getElementById("duration");

    const volumeControl =
        document.getElementById("volume-control");


    /*
     * =========================================================
     * SONG DATA
     *
     * Data comes from HTML data-* attributes.
     * =========================================================
     */

    const songElements =
        document.querySelectorAll(".song-item");


    const songs = Array.from(songElements).map(
        function (element) {

            return {
                id: element.dataset.songId,
                title: element.dataset.title,
                artists: element.dataset.artists,
                category: element.dataset.category,
                url: element.dataset.url
            };

        }
    );


    /*
     * =========================================================
     * PLAYER STATE
     * =========================================================
     */

    let currentIndex = -1;


    /*
     * =========================================================
     * FORMAT TIME
     * =========================================================
     */

    function formatTime(seconds) {

        if (isNaN(seconds)) {
            return "0:00";
        }

        const minutes =
            Math.floor(seconds / 60);

        const remainingSeconds =
            Math.floor(seconds % 60)
                .toString()
                .padStart(2, "0");

        return `${minutes}:${remainingSeconds}`;
    }


    /*
     * =========================================================
     * PLAY SONG
     * =========================================================
     */

    function playSong(index) {

        if (
            index < 0 ||
            index >= songs.length
        ) {
            return;
        }


        currentIndex = index;


        const song =
            songs[currentIndex];


        audioPlayer.src =
            song.url;


        playerTitle.textContent =
            song.title;


        playerArtist.textContent =
            `${song.artists} • ${song.category}`;


        audioPlayer.play();


        updatePlayButton();


        updateActiveSong();

    }


    /*
     * =========================================================
     * UPDATE PLAY / PAUSE BUTTON
     * =========================================================
     */

    function updatePlayButton() {

        if (audioPlayer.paused) {

            playerPlayButton.innerHTML =
                '<i class="bi bi-play-fill"></i>';

        } else {

            playerPlayButton.innerHTML =
                '<i class="bi bi-pause-fill"></i>';

        }

    }


    /*
     * =========================================================
     * HIGHLIGHT CURRENT SONG
     * =========================================================
     */

    function updateActiveSong() {

        songElements.forEach(
            function (element) {

                element.classList.remove(
                    "active-song"
                );

            }
        );


        if (currentIndex < 0) {
            return;
        }


        const currentSong =
            songs[currentIndex];


        const currentElement =
            document.querySelector(
                `[data-song-id="${currentSong.id}"]`
            );


        if (currentElement) {

            currentElement.classList.add(
                "active-song"
            );

        }

    }


    /*
     * =========================================================
     * SONG CARD PLAY BUTTONS
     * =========================================================
     */

    document
        .querySelectorAll(".play-song")
        .forEach(
            function (button, index) {

                button.addEventListener(
                    "click",
                    function () {

                        playSong(index);

                    }
                );

            }
        );


    /*
     * =========================================================
     * PLAY / PAUSE
     * =========================================================
     */

    playerPlayButton.addEventListener(
        "click",
        function () {

            if (currentIndex === -1) {

                if (songs.length > 0) {
                    playSong(0);
                }

                return;
            }


            if (audioPlayer.paused) {

                audioPlayer.play();

            } else {

                audioPlayer.pause();

            }

        }
    );


    /*
     * =========================================================
     * NEXT SONG
     * =========================================================
     */

    nextButton.addEventListener(
        "click",
        function () {

            if (songs.length === 0) {
                return;
            }


            let nextIndex =
                currentIndex + 1;


            if (nextIndex >= songs.length) {
                nextIndex = 0;
            }


            playSong(nextIndex);

        }
    );


    /*
     * =========================================================
     * PREVIOUS SONG
     * =========================================================
     */

    previousButton.addEventListener(
        "click",
        function () {

            if (songs.length === 0) {
                return;
            }


            let previousIndex =
                currentIndex - 1;


            if (previousIndex < 0) {

                previousIndex =
                    songs.length - 1;

            }


            playSong(previousIndex);

        }
    );


    /*
     * =========================================================
     * AUTOMATIC NEXT SONG
     * =========================================================
     */

    audioPlayer.addEventListener(
        "ended",
        function () {

            if (songs.length === 0) {
                return;
            }


            let nextIndex =
                currentIndex + 1;


            if (nextIndex >= songs.length) {
                nextIndex = 0;
            }


            playSong(nextIndex);

        }
    );


    /*
     * =========================================================
     * AUDIO EVENTS
     * =========================================================
     */

    audioPlayer.addEventListener(
        "play",
        function () {

            updatePlayButton();

        }
    );


    audioPlayer.addEventListener(
        "pause",
        function () {

            updatePlayButton();

        }
    );


    /*
     * =========================================================
     * AUDIO METADATA
     * =========================================================
     */

    audioPlayer.addEventListener(
        "loadedmetadata",
        function () {

            durationElement.textContent =
                formatTime(audioPlayer.duration);

        }
    );


    /*
     * =========================================================
     * PROGRESS
     * =========================================================
     */

    audioPlayer.addEventListener(
        "timeupdate",
        function () {

            if (!audioPlayer.duration) {
                return;
            }


            const percentage =
                (
                    audioPlayer.currentTime /
                    audioPlayer.duration
                ) * 100;


            progressBar.value =
                percentage;


            currentTimeElement.textContent =
                formatTime(
                    audioPlayer.currentTime
                );

        }
    );


    /*
     * =========================================================
     * SEEK
     * =========================================================
     */

    progressBar.addEventListener(
        "input",
        function () {

            if (!audioPlayer.duration) {
                return;
            }


            audioPlayer.currentTime =
                (
                    this.value / 100
                ) * audioPlayer.duration;

        }
    );


    /*
     * =========================================================
     * VOLUME
     * =========================================================
     */

    volumeControl.addEventListener(
        "input",
        function () {

            audioPlayer.volume =
                this.value;

        }
    );

});