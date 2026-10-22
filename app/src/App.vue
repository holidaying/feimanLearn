<script>
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { loadDaily } from './store.js'

export default {
  onLaunch() {
    loadDaily()
  },
  onShow() {},
  onHide() {}
}
</script>

<style>
/* ============ 费曼实验课 · 设计系统（移动端） ============
   实验记录本 · 暖白纸感 + 墨黑衬线 + 单一琥珀强调色
   注意：uni-app App 端为 webview 渲染，CSS 变量可用；勿在 <style> 内写 #ifdef / @media
   ======================================================== */
page {
  --paper: #F6F2E9;
  --paper-raised: #FFFDF8;
  --paper-sunken: #EFE9DC;
  --ink: #191712;
  --ink-2: #4A443A;
  --ink-3: #8A8272;
  --rule: #DED5C2;
  --rule-2: #CFC5AF;
  --accent: #B4451A;
  --accent-ink: #8C3413;
  --accent-soft: #F7E6DC;
  --teal: #0F6B60;
  --teal-soft: #DFF0ED;

  --font-display: "Songti SC", "SimSun", "Source Han Serif SC", serif;
  --font-body: -apple-system, "PingFang SC", "Helvetica Neue", "Microsoft YaHei", sans-serif;
  --font-mono: "SF Mono", "Menlo", "Consolas", monospace;

  --r-sm: 6rpx;
  --r-md: 12rpx;

  background: var(--paper);
  color: var(--ink);
  font-family: var(--font-body);
  font-size: 30rpx;
  line-height: 1.7;
}

/* 细网格纸纹 */
page::before {
  content: "";
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(25, 23, 18, 0.028) 1rpx, transparent 1rpx),
    linear-gradient(90deg, rgba(25, 23, 18, 0.028) 1rpx, transparent 1rpx);
  background-size: 56rpx 56rpx;
  z-index: 0;
}

.page {
  position: relative;
  z-index: 1;
  padding: 36rpx 40rpx 80rpx;
}

/* ---------- 文字 ---------- */
.display {
  font-family: var(--font-display);
  font-size: 68rpx;
  font-weight: 700;
  line-height: 1.16;
  letter-spacing: -0.02em;
  color: var(--ink);
}
.display-sm {
  font-family: var(--font-display);
  font-size: 48rpx;
  font-weight: 700;
  line-height: 1.28;
  color: var(--ink);
}
.eyebrow {
  font-family: var(--font-mono);
  font-size: 22rpx;
  letter-spacing: 0.1em;
  color: var(--ink-3);
  margin: 0 0 20rpx;
}
.mono { font-family: var(--font-mono); font-size: 22rpx; }
.mono-lg { font-family: var(--font-mono); font-size: 26rpx; font-weight: 700; }
.muted { color: var(--ink-2); }
.muted-2 { color: var(--ink-3); }
.pull {
  font-family: var(--font-display);
  font-size: 32rpx;
  line-height: 1.7;
  color: var(--ink-2);
}

/* ---------- 容器 ---------- */
.panel {
  background: var(--paper-raised);
  border: 1rpx solid var(--rule);
  border-radius: var(--r-md);
  padding: 32rpx;
}
.rule { height: 1rpx; background: var(--rule); margin: 40rpx 0; }

/* ---------- 按钮 ---------- */
.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--accent);
  color: #FFF8F0;
  border: 0;
  border-radius: var(--r-md);
  padding: 22rpx 40rpx;
  font-size: 30rpx;
  font-weight: 700;
  letter-spacing: 0.02em;
}
.btn-primary::after { border: 0; }
.btn-primary[disabled] { opacity: 0.45; }

.btn-ghost {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: var(--ink-2);
  border: 1rpx solid var(--rule-2);
  border-radius: var(--r-md);
  padding: 20rpx 32rpx;
  font-size: 28rpx;
}
.btn-ghost::after { border: 0; }

.btn-xl { padding: 30rpx 48rpx; font-size: 32rpx; width: 100%; }
.btn-sm { padding: 12rpx 24rpx; font-size: 24rpx; }

/* ---------- 标签 ---------- */
.tag {
  display: inline-block;
  font-family: var(--font-mono);
  font-size: 20rpx;
  padding: 4rpx 16rpx;
  border-radius: 999rpx;
  background: var(--paper-sunken);
  color: var(--ink-3);
}
.tag-hot { background: var(--accent-soft); color: var(--accent-ink); }
.tag-base { background: var(--teal-soft); color: var(--teal); }

/* ---------- 入场编排 ---------- */
.anim { opacity: 0; animation: rise 520ms cubic-bezier(0.16, 1, 0.3, 1) both; }
@keyframes rise {
  from { opacity: 0; transform: translateY(20rpx); }
  to { opacity: 1; transform: none; }
}
.d1 { animation-delay: 40ms; }
.d2 { animation-delay: 110ms; }
.d3 { animation-delay: 180ms; }
.d4 { animation-delay: 250ms; }
.d5 { animation-delay: 320ms; }
.d6 { animation-delay: 390ms; }
</style>
