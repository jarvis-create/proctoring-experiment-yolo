<template>
    <div class="container mx-auto p-4 relative min-h-screen">
        <div class="bg-white shadow-xl rounded-lg overflow-hidden">
            <div class="p-6">
                <h2 class="text-2xl font-bold text-gray-800 mb-4">
                    Exam Proctor
                </h2>

                <div v-if="!isExamStarted" class="text-center">
                    <button
                        @click="startExam"
                        class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition duration-300 ease-in-out"
                    >
                        Start Exam
                    </button>
                </div>

                <div v-else>
                    <vue-countdown
                        :time="endTimeInSeconds * 1000"
                        v-slot="{ hours, minutes, seconds }"
                        @end="onCountdownEnd"
                        @progress="onCountdownProgress"
                    >
                        <div
                            class="flex items-center w-1/5 my-3 font-bold bg-gray-200 p-2 rounded-md"
                        >
                            <Clock class="mr-2" />
                            {{ hours }}H, {{ minutes }}M, {{ seconds }}S
                        </div>
                    </vue-countdown>
                    <div
                        v-if="currentQuestionIndex < questions.length"
                        class="mb-6"
                    >
                        <h3 class="text-xl font-semibold mb-4">
                            Question {{ currentQuestionIndex + 1 }}
                        </h3>
                        <p class="mb-4">
                            {{ questions[currentQuestionIndex].question }}
                        </p>
                        <div class="space-y-2">
                            <div
                                v-for="(option, index) in questions[
                                    currentQuestionIndex
                                ].options"
                                :key="index"
                            >
                                <label class="flex items-center space-x-2">
                                    <input
                                        type="radio"
                                        :value="option"
                                        v-model="selectedAnswer"
                                        class="form-radio text-blue-600"
                                    />
                                    <span>{{ option }}</span>
                                </label>
                            </div>
                        </div>
                        <button
                            @click="submitAnswer"
                            class="mt-4 bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded transition duration-300 ease-in-out"
                            :disabled="!selectedAnswer"
                        >
                            Submit Answer
                        </button>
                    </div>
                    <div v-else class="text-center">
                        <p class="mb-4 text-lg">
                            You have completed all questions.
                        </p>
                        <button
                            @click="endExam"
                            class="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded transition duration-300 ease-in-out"
                        >
                            End Exam
                        </button>
                    </div>
                </div>

                <div v-if="warnings.length > 0" class="mt-4 space-y-2">
                    <div
                        v-for="(warning, index) in warnings"
                        :key="index"
                        class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded"
                    >
                        <div class="flex items-center">
                            <AlertCircle class="h-5 w-5 mr-2" />
                            <p class="font-bold">Warning</p>
                        </div>
                        <p>{{ warning }}</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Video stream in bottom right corner -->
        <div
            class="fixed bottom-4 right-4 w-48 h-36 bg-gray-700 rounded-lg overflow-hidden"
            :class="{
                'opacity-100': isExamStarted,
                'opacity-0': !isExamStarted,
            }"
        >
            <!-- Face detection canvas overlay -->
            <canvas
                ref="canvasElement"
                class="absolute top-0 left-0 w-full h-full pointer-events-none bg-black/90"
            ></canvas>
            <video
                ref="videoElement"
                autoplay
                muted
                class="w-full h-full object-cover"
            ></video>
        </div>
    </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from "vue";
import { AlertCircle, Clock } from "lucide-vue-next";
// import { useMouse } from "@vueuse/core";
import VueCountdown from "@chenfengyuan/vue-countdown";

const SERVER_URL = process.env.SERVER_URL || "http://localhost:8000";
const DETECT_FACES_ENDPOINT = `${SERVER_URL}/analyze`;

const assessment = {
    id: "1",
    name: "Common Affairs",
    categories: ["General Knowledge", "Math", "Science"],
    skill_tests: [],
    general_questions: [
        {
            question: "What is the capital of France?",
            options: ["London", "Berlin", "Paris", "Madrid"],
        },
        {
            question: "Which planet is known as the Red Planet?",
            options: ["Venus", "Mars", "Jupiter", "Saturn"],
        },
        {
            question: "Who painted the Mona Lisa?",
            options: [
                "Vincent van Gogh",
                "Pablo Picasso",
                "Leonardo da Vinci",
                "Michelangelo",
            ],
        },
        {
            question: "What is the largest ocean on Earth?",
            options: [
                "Atlantic Ocean",
                "Indian Ocean",
                "Arctic Ocean",
                "Pacific Ocean",
            ],
        },
    ],
    duration_in_seconds: 300,
};

const endTimeInSeconds = ref(assessment.duration_in_seconds); // 30 seconds
const warningTimeInSeconds = ref((10 / 100) * assessment.duration_in_seconds); // 10 seconds

const isExamStarted = ref(false);
const warnings = ref([]);
const currentQuestionIndex = ref(0);
const selectedAnswer = ref("");
const isTabActive = ref(true);
const videoElement = ref(null);
const canvasElement = ref(null);

let stream = null;
let detectionInterval = null;

const lastPingTime = ref(0);
const timeBetweenPings = ref(10000); // 10 seconds

const questions = ref(assessment.general_questions);

const startVideoStream = async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: true,
        });
        if (videoElement.value) {
            videoElement.value.srcObject = stream;
        }
    } catch (error) {
        console.error("Error accessing camera:", error);
        addWarning("Unable to access camera");
    }
};

async function sendImageToBackend() {
    if (!isExamStarted.value) {
        return; // Exit the function if the exam hasn't started
    }

    if (!canvasElement.value || !videoElement.value) {
        return;
    }

    const currentTime = Date.now();

    if (currentTime - lastPingTime.value > timeBetweenPings.value) {
        lastPingTime.value = currentTime;

        const canvas = canvasElement.value;
        canvas.width = videoElement.value.videoWidth;
        canvas.height = videoElement.value.videoHeight;
        canvas
            .getContext("2d", { alpha: false })
            .drawImage(videoElement.value, 0, 0, canvas.width, canvas.height);

        canvas.toBlob(async (blob) => {
            const file = new File(
                [blob],
                `${assessment.id}-${Date.now()}.jpg`,
                {
                    type: "image/jpg",
                },
            );

            const formData = new FormData();
            formData.append("file", file);

            try {
                const response = await fetch(DETECT_FACES_ENDPOINT, {
                    method: "POST",
                    body: formData,
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const responseData = await response.json();
                console.log(responseData);

                if (responseData.error) {
                    console.error(responseData.error);
                }

                if (responseData.phone_detected) {
                    addWarning("Phone detected");
                    simulateApiPost("phone_detected", { detected: true });
                }

                if (responseData.multiple_faces_detected) {
                    addWarning("Multiple faces detected");
                    simulateApiPost("multiple_faces_detected", {
                        detected: true,
                    });
                }

                if (responseData.looking_away) {
                    addWarning("Looking away");
                    simulateApiPost("looking_away", { detected: true });
                }
            } catch (error) {
                console.error("Error sending image to backend:", error);
            }
        }, "image/png");
    }
}

const onCountdownEnd = () => {
    endExam();
};

const onCountdownProgress = (data) => {
    if (data.seconds === warningTimeInSeconds.value) {
        addWarning(`Only ${data.seconds} seconds left`);
    }
};

const stopVideoStream = () => {
    if (videoElement.value && videoElement.value.srcObject) {
        const tracks = videoElement.value.srcObject.getTracks();
        tracks.forEach((track) => track.stop());
    }
};

const startMonitoring = () => {
    monitorFaces();
    monitorPhones();
    monitorTabSwitches();
    monitorGaze();
};

const stopMonitoring = () => {
    // Stop all monitoring processes here
    // This would involve clearing any intervals or removing event listeners
};

const monitorFaces = () => {
    // Simulating face detection every 5 seconds
};

const monitorPhones = () => {
    // Simulating phone detection every 7 seconds
};

const monitorTabSwitches = () => {
    const handleVisibilityChange = () => {
        if (document.hidden && isTabActive.value) {
            isTabActive.value = false;
            addWarning("Tab switch detected");
            simulateApiPost("tab_switch", { switched: true });
        } else if (!document.hidden) {
            isTabActive.value = true;
        }
    };
    document.addEventListener("visibilitychange", handleVisibilityChange);
    onUnmounted(() => {
        document.removeEventListener(
            "visibilitychange",
            handleVisibilityChange,
        );
    });
};

const monitorGaze = () => {
    // Simulating gaze tracking every 3 seconds
};

const addWarning = (warning) => {
    warnings.value.push(warning);
};

const startExam = () => {
    isExamStarted.value = true;
    startVideoStream();
    startMonitoring();
};

const submitAnswer = () => {
    simulateApiPost("submit_answer", {
        questionIndex: currentQuestionIndex.value,
        answer: selectedAnswer.value,
    });
    currentQuestionIndex.value++;
    selectedAnswer.value = "";
};

const endExam = () => {
    isExamStarted.value = false;
    stopVideoStream();
    stopMonitoring();
    currentQuestionIndex.value = 0;
    selectedAnswer.value = "";
    warnings.value = [];
    simulateApiPost("end_exam", { totalQuestions: questions.length });
};

const simulateApiPost = (endpoint, data) => {
    console.log(`POST to /${endpoint}:`, data);
};

async function startVideo() {
    stream = await navigator.mediaDevices.getUserMedia({ video: {} });

    if (videoElement.value) {
        videoElement.value.srcObject = stream;
    }
}

function stopVideo() {
    if (stream) {
        stream.getTracks().forEach((track) => track.stop());
    }
}

onMounted(async () => {
    await startVideo();

    detectionInterval = setInterval(
        async () => await sendImageToBackend(),
        timeBetweenPings,
    );
});

onUnmounted(() => {
    stopVideo();
    stopMonitoring();
    stopVideoStream();
    if (detectionInterval.value) {
        clearInterval(detectionInterval.value);
    }
});
</script>
