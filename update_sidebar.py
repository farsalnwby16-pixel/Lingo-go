import re
import os

index_path = 'templates/index.html'

if os.path.exists(index_path):
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # New category HTML block
    new_category_html = '''
        <!-- قسم القصص التفاعلية -->
        <div class="menu-item">
            <button class="accordion-btn" onclick="toggleAccordion(this)">
                ▼ 📖 القصص التفاعلية (Interactive Stories)
            </button>
            <div class="panel">
                <div class="level-grid">
                    <a href="/?cat=القصص التفاعلية (Interactive Stories)&level=A1" class="level-btn">A1</a>
                    <a href="/?cat=القصص التفاعلية (Interactive Stories)&level=A2" class="level-btn">A2</a>
                    <a href="/?cat=القصص التفاعلية (Interactive Stories)&level=B1" class="level-btn">B1</a>
                    <a href="/?cat=القصص التفاعلية (Interactive Stories)&level=B2" class="level-btn">B2</a>
                    <a href="/?cat=القصص التفاعلية (Interactive Stories)&level=C1" class="level-btn">C1</a>
                    <a href="/?cat=القصص التفاعلية (Interactive Stories)&level=C2" class="level-btn">C2</a>
                </div>
            </div>
        </div>
    '''

    # Audio Lab Widget block to append below lesson content
    audio_lab_html = '''
    {% if current_lesson and current_lesson.story_text %}
    <div id="recordingLab" style="background:#1c2541; border:1px solid #3a506b; border-radius:12px; padding:15px; margin-top:20px; color:#fff;">
        <h3 style="color:#6fffe9; margin-top:0; font-size:1.1rem; text-align:center;">🎙️ مختبر التحدث والتقييم الذكي</h3>
        <p style="color:#94a3b8; font-size:0.85rem; text-align:center;">اقرأ نص القصة بصوتك واضغط إيقاف للحصول على تقييم نطقك فوراً</p>
        
        <div style="display:flex; justify-content:center; gap:10px; margin:15px 0;">
            <button id="startRecBtn" onclick="startStoryRecording()" style="background:#10b981; color:#fff; border:none; padding:10px 18px; border-radius:8px; font-weight:bold; cursor:pointer;">▶️ بدء التسجيل والتحدث</button>
            <button id="stopRecBtn" onclick="stopStoryRecording()" style="background:#ef4444; color:#fff; border:none; padding:10px 18px; border-radius:8px; font-weight:bold; cursor:pointer; display:none;">⏹️ إيقاف وحساب التقييم</button>
        </div>

        <div style="text-align:center; margin-bottom:10px;">
            <audio id="audioPlayback" controls style="width:100%; max-width:400px; display:none; margin:0 auto;"></audio>
        </div>

        <div id="evalResult"></div>
    </div>

    <script>
    let recognition;
    let mediaRecorder;
    let audioChunks = [];
    let recognizedSpokenText = "";

    function startStoryRecording() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert("متصفحك لا يدعم التعرف على الصوت المباشر. يفضل استخدام متصفح Chrome.");
            return;
        }

        recognizedSpokenText = "";
        audioChunks = [];

        recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onresult = (event) => {
            let text = "";
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                text += event.results[i][0].transcript;
            }
            recognizedSpokenText = text;
        };

        recognition.start();

        navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
            mediaRecorder.onstop = () => {
                const blob = new Blob(audioChunks, { type: 'audio/webm' });
                const audioURL = URL.createObjectURL(blob);
                const player = document.getElementById('audioPlayback');
                player.src = audioURL;
                player.style.display = 'block';
                evaluatePronunciation();
            };
            mediaRecorder.start();
            
            document.getElementById('startRecBtn').style.display = 'none';
            document.getElementById('stopRecBtn').style.display = 'inline-block';
            document.getElementById('evalResult').innerHTML = '<p style="color:#eab308; text-align:center;">جارٍ استماع صوتك وتسجيله... تكلم الآن!</p>';
        }).catch(err => {
            alert("يرجى إعطاء الإذن للمتصفح لاستخدام الميكروفون.");
        });
    }

    function stopStoryRecording() {
        if (recognition) recognition.stop();
        if (mediaRecorder && mediaRecorder.state !== "inactive") mediaRecorder.stop();
        
        document.getElementById('startRecBtn').style.display = 'inline-block';
        document.getElementById('stopRecBtn').style.display = 'none';
    }

    function evaluatePronunciation() {
        const storyText = {{ current_lesson.story_text|tojson }};
        if (!storyText || !storyText.trim()) return;

        if (!recognizedSpokenText.trim()) {
            document.getElementById('evalResult').innerHTML = '<p style="color:#ef4444; text-align:center;">لم يتلق المنبه أي صوت واضح، أعد المحاولة وتحدث بوضوح.</p>';
            return;
        }

        const cleanOrig = storyText.toLowerCase().replace(/[^\\w\\s]/g, '').split(/\\s+/).filter(w => w.length > 0);
        const cleanSpoken = recognizedSpokenText.toLowerCase().replace(/[^\\w\\s]/g, '').split(/\\s+/).filter(w => w.length > 0);

        let matchCount = 0;
        let missedWords = [];

        cleanOrig.forEach(word => {
            if (cleanSpoken.includes(word)) {
                matchCount++;
            } else {
                if (!missedWords.includes(word)) missedWords.push(word);
            }
        });

        let score = Math.round((matchCount / cleanOrig.length) * 100);
        if (score > 100) score = 100;

        let strength = score >= 75 ? "ممتاز جداً! مخارج الكلمات واضحة ومطابقة للنص بشكل قوي." : "أداء جيد، استطعت نطق جزء جيد من القصة.";
        let weakness = missedWords.length > 0 ? "كلمات تحتاج إعادة تدرب: " + missedWords.slice(0, 6).join(', ') : "ممتاز! لم يتم رصد أي أخطاء بصرية أو نطقية.";

        document.getElementById('evalResult').innerHTML = `
            <div style="background:#0b132b; padding:15px; border-radius:10px; border:1px solid #6fffe9; margin-top:10px;">
                <div style="font-size:1.3rem; font-weight:bold; color:#6fffe9; text-align:center; margin-bottom:8px;">
                    📊 نسبة التقييم: ${score}%
                </div>
                <p style="color:#10b981; margin:6px 0; font-size:0.9rem;"><strong>💪 نقاط القوة:</strong> ${strength}</p>
                <p style="color:#f59e0b; margin:6px 0; font-size:0.9rem;"><strong>🔧 نقاط التطوير:</strong> ${weakness}</p>
                <p style="color:#94a3b8; font-size:0.78rem; margin-top:8px;">النص الذي تم التقاطه: "${recognizedSpokenText}"</p>
            </div>
        `;
    }
    </script>
    {% endif %}
    '''

    # Inject new category if not existing
    if 'القصص التفاعلية' not in content:
        # insert before end of sidebar menu
        content = content.replace('<!-- Shadowing section or end of menu -->', new_category_html)
        if 'القصص التفاعلية' not in content:
            # Fallback insertion
            content = content.replace('</div>\n    </div>\n    <div class="user-profile"', new_category_html + '\n</div>\n    </div>\n    <div class="user-profile"')
            if 'القصص التفاعلية' not in content:
                content = content.replace('</aside>', new_category_html + '\n</aside>')

    if 'recordingLab' not in content:
        content = content.replace('</main>', audio_lab_html + '\n</main>')

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ تم إضافة قسم القصص التفاعلية للقائمة الجانبية بنجاح!")
else:
    print("❌ لم يتم العثور على templates/index.html")

