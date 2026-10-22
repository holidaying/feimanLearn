// 费曼实验课 · 语音识别适配层
// App 端走 5+ plus.speech（原生识别，需在 manifest app-plus.modules 声明 "Speech"）
// H5 端降级为 Web Speech API（仅 Chrome / Edge）
//
// 统一对外只暴露三个动作：start / stop / isSupported

let recog = null      // H5 识别实例
let shouldListen = false // 用户意图（与 UI 状态分离，避免自动重连把状态打回）

function isApp() {
  return typeof plus !== 'undefined' && plus.speech
}

export function isSupported() {
  if (isApp()) return true
  const SR = typeof window !== 'undefined' && (window.SpeechRecognition || window.webkitSpeechRecognition)
  return !!SR
}

function ensurePermission() {
  return new Promise((resolve) => {
    if (!isApp() || !plus.android) return resolve(true)
    plus.android.requestPermissions(
      ['android.permission.RECORD_AUDIO'],
      (res) => resolve(res && res.granted && res.granted.length > 0 ? true : res.deniedPresent !== true),
      () => resolve(false)
    )
  })
}

/**
 * 开始识别
 * @param {Object} opt { onPartial(text), onFinal(text), onEnd(), onError(msg) }
 */
export async function start(opt = {}) {
  const { onPartial, onFinal, onEnd, onError } = opt
  shouldListen = true

  if (isApp()) {
    const ok = await ensurePermission()
    if (!ok) { onError && onError('未获得录音权限'); return }

    plus.speech.addEventListener('recognizing', (e) => {
      if (shouldListen && e && e.partialResult) onPartial && onPartial(e.partialResult)
    })
    plus.speech.addEventListener('recognition', (e) => {
      if (shouldListen && e && e.result) onFinal && onFinal(e.result)
    })
    plus.speech.addEventListener('end', () => {
      onEnd && onEnd()
      if (shouldListen) {
        // 原生识别默认单句结束，用户没点停就继续
        try { plus.speech.startRecognize({ engine: 'baidu', lang: 'zh-cn', continue: true, interimResults: true }) } catch (e) {}
      }
    })
    plus.speech.addEventListener('error', (e) => {
      onError && onError((e && e.message) || '识别出错')
      onEnd && onEnd()
    })
    try {
      plus.speech.startRecognize({ engine: 'baidu', lang: 'zh-cn', continue: true, interimResults: true })
    } catch (e) {
      onError && onError('无法启动语音识别')
    }
    return
  }

  // ---- H5 ----
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SR) { onError && onError('当前环境不支持语音输入，请直接打字'); return }

  recog = new SR()
  recog.lang = 'zh-CN'
  recog.continuous = true
  recog.interimResults = true
  let acc = ''

  recog.onresult = (ev) => {
    let interim = ''
    for (let i = ev.resultIndex; i < ev.results.length; i++) {
      const t = ev.results[i][0].transcript
      if (ev.results[i].isFinal) acc += t
      else interim += t
    }
    onPartial && onPartial(acc + interim)
  }
  recog.onerror = (ev) => { onError && onError(ev.error || '识别出错') }
  recog.onend = () => {
    onEnd && onEnd()
    if (shouldListen) { try { recog.start() } catch (e) {} }
  }
  try { recog.start() } catch (e) { onError && onError('无法启动语音识别') }
}

export function stop() {
  shouldListen = false
  try {
    if (isApp()) plus.speech.stopRecognize()
    else if (recog) recog.abort()
  } catch (e) {}
  recog = null
}
