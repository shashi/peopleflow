(function () {

var nbyte_digest = function (str, n) {
    var dig = Sha1.hash(str)

    if (dig.length >= n) {
        return dig.substring(0, n)
    } else {
        return dig + nbyte_digest(dig, n - dig.length)
    }
}

var decryptObject = function (encrypted, secret) {
    var key = CryptoJS.enc.Hex.parse(secret),
        iv = CryptoJS.enc.Hex.parse(encrypted.iv),
        cipher = CryptoJS.lib.CipherParams.create({
            ciphertext: CryptoJS.enc.Base64.parse(
                            encrypted.ciphertext
            )
        }),
        result = CryptoJS.AES.decrypt(
            cipher, key, {iv: iv, mode: CryptoJS.mode.CFB}
        )
    
    return JSON.parse(result.toString(CryptoJS.enc.Utf8))
}

var decryptParticipant = function (encrypted, secret) {
    return decryptObject(encrypted, nbyte_digest(secret, 32))
}

var getParticipantCryptext = function (public) {
    return getLocalStorageObject(
        makePath("participants", "encrypted"),
        public
    )
}

var getParticipantFromBarcode = function (code) {
    var public = code.substring(0, N_PUBLIC),
        secret = code.substring(N_PUBLIC),
        cryptext = getParticipantCryptext(public)

    if (cryptext === null) {
        return null // This should show a dialog
    } else {
        var participant = decryptParticipant(cryptext, secret)
            console.log(participant)
        participant.public = public
        participant.secret = secret
        return participant
    }
}

var isObjectEmpty = function (obj) {
    for (var key in obj) {
        if (obj.hasOwnProperty(key)) return false
    }
    return true
}

var addJitter = function (num, jitter_max) {
    return num + (0.5 - Math.random()) * jitter_max
}

var makePath = function (ns, key) {
    return ns + "/" + key
}

var getLocalStorageObject = function (ns, key, obj) {
    var json = window.localStorage.getItem(makePath(ns, key))
    if (json === null) {
        return null
    }
    return JSON.parse(json)
}

var setLocalStorageObject = function (ns, key, obj) {
    window.localStorage.setItem(
        makePath(ns, key),
        JSON.stringify(obj)
    )
}

var getLocalStorageNS = function (ns) {
    var prefix = makePath(ns, "")
        var objects = {}

    for (var key in window.localStorage){
        if (key.indexOf(prefix) == 0){
            objects[key] = window.localStorage.getItem(key)
        }
    }
}

var clearLocalStorageObject = function (ns, key) {
    window.localStorage.removeItem(makePath(ns, key))
}

var clearLocalStorageNS = function (ns) {
    // Scary shit.
    var prefix = makePath(ns, "")
    for (var key in window.localStorage){
        if (key.indexOf(prefix) == 0){
            window.localStorage.removeItem(key);
        }
    }
}

var getLocalStorageArray = function (ns, key) {
    var arr = getLocalStorageObject(ns, key)
    if (arr === null) {
        return null
    }
    if (arr.constructor != Array) {
        throw("Item at " + makePath(ns, key) + " is not an array!")
    }
    return arr
}

var setLocalStorageArray = function (ns, key, arr) {
    if (arr.constructor != Array) {
        throw("Item cannot be set as an array at " +
                makePath(ns, key))
    }
    setLocalStorageObject(ns, key, arr)
}

var addToSyncQueue = function (id, secret) {
    var queue = getLocalStorageObject("participants", "sync_queue")
    if (queue === null) {
        queue = {}
    }
    queue[id] = secret;
    setLocalStorageObject("participants", "sync_queue", queue)
}

var showErrorMessage = function (msg) {
    $("#error-box").modal('show')
    $("#error-msg").html(msg)
    setTimeout(function () { $("#error-box").modal('hide') }, 3000)
}

var showMessageAndProceed = function (participant, fn) {
    var TIMEOUT = 5000
    $("#greetings").text("Hi " + participant.name + "!")
    $("#share-countdown").text(5)

    var countdown = setInterval(function () {
        var cdown = $("#share-countdown")
        cdown.text(Number(cdown.text()) - 1)
    }, 1000)

    setTimeout(function () {
        $("#message-box").modal('hide')
        clearInterval(countdown)
    }, TIMEOUT)

    // (spam) bomb planted!
    var ticktock = setTimeout(fn, TIMEOUT)

    $("#cancel-share").unbind("click")
    $("#cancel-share").bind("click", function () {
        // bomb diffused
        clearTimeout(ticktock)
        clearInterval(countdown)
        $("#message-box").modal("hide")
    })

    $("#message-box").modal('show')
}

var doSyncEntries = function () {
    var queue = getLocalStorageObject("participants", "sync_queue")
    // send this object to the endpoint
    // response contains approved participants, and rejected ones
    // clear queue
    $.ajax({
        type: "POST",
        //the url where you want to sent the userName and password to
        url: SHARED_SYNC_URL,
        dataType: 'json',
        //json object to sent to the authentication url
        data: JSON.stringify(queue),
        success: function (data) {
            var new_queue = getLocalStorageObject(
                "participants", "sync_queue")

            for (var key in data) {
                if (!data.hasOwnProperty(key)) {
                    continue
                }
                if (data[key] == 503) {
                    // Some kind of database unavailability problem
                    continue
                }
                delete new_queue[key]
            }
            setLocalStorageObject(
                "participants", "sync_queue", new_queue)
            console.log("Synced.", data)
        }
    })
}

var doTap = function (code) {
    //console.log("Tapped: " + code);
    var participant = getParticipantFromBarcode(code)
    // log participant data for this kiosk
    if (participant == null) {
        showErrorMessage(
               "Looks like it's an invalid barcode! <br>" +
               "Try again if you are sure it isn't invalid...")
        return
    }
    var entry = {
        timestamp: (new Date).toISOString(),
        public: participant.public,
        data: participant
    }
    showMessageAndProceed(
            participant,
            function () {
                // First log this in the client side.
                setLocalStorageObject(
                    makePath("participants", "decrypted"),
                        participant.id, entry)

                addToSyncQueue(participant.id, participant.secret)
                doSyncEntries()
            }
    )
}

// Keyboard input state machine
var codeAcc = "",
    prevTimeout = null
window.addEventListener("keypress", function (ev) {
    var chr = String.fromCharCode(ev.keyCode),
        chrCode = ev.keyCode
    if (chrCode == END_CHAR) {
        doTap(codeAcc)
        codeAcc = ""
        clearTimeout(prevTimeout)
    } else {
        codeAcc = codeAcc + chr
        console.log(codeAcc)
        clearTimeout(prevTimeout)
        prevTimeout = setTimeout(
            function () { codeAcc ="" },
            RESET_AFTER
        )
    }
});

var refreshParticipants = function(){
    $.getJSON(PARTICIPANTS_URL, function(data){
        if(data['error']) {
            toasttr.error(
                    "Participants not synced with server.",
                    "There is a connectivity problem."
                    )
        } else {
            // First remove participant localStorage
            clearLocalStorageNS(
                makePath("participants", "encrypted"))
            participants = data['participants']
            // Re fill participant localStorage
            for (var key in participants){
                if (!participants.hasOwnProperty(key)){
                    continue;
                } 
                console.log("storing ", participants[key])
                setLocalStorageObject(
                    makePath("participants", "encrypted"),
                    key,
                    participants[key]
                )
            }
        }
    })
}

$(document).ready(function(){
  var img = $('#contact_point #company .logo img')
  img.css({'margin-top': -img.height()/2, 'top': '50%'})
  refreshParticipants()

  setInterval(
      refreshParticipants,
      addJitter(REFRESH_TIMEOUT, REFRESH_JITTER))

  setInterval(function () {
      if (isObjectEmpty(
              getLocalStorageObject("participants", "sync_queue")
          )) {
          doSyncEntries()
      }
  }, addJitter(REFRESH_TIMEOUT, REFRESH_JITTER))
});

// Anything else to export?
window.getLocalStorageNS = getLocalStorageNS
window.getParticipantFromBarcode = getParticipantFromBarcode
window.doTap = doTap

})()
