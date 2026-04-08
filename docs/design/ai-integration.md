# AI建议功能设计 - DeepSeek API方案

> 创建时间：2026-04-05  
> 决策：使用DeepSeek API + 模板兜底机制

---

## 1. 方案选择理由

| 方案 | 优点 | 缺点 | 选择结果 |
|------|------|------|---------|
| Claude API | 效果最佳 | 需代理，成本高 | ❌ |
| **DeepSeek API** | 国内可用，性价比高，中文好 | 需网络配置 | ✅ |
| 国产模型(GLM等) | 国内稳定 | 效果参差 | ❌ |
| 纯模板 | 零成本 | 不够智能 | ⚠️ 作为兜底 |

---

## 2. DeepSeek API接入设计

### 2.1 后端配置

```python
# settings.py 配置
DEEPSEEK_CONFIG = {
    'api_key': os.environ.get('DEEPSEEK_API_KEY'),
    'api_base': 'https://api.deepseek.com/v1',
    'model': 'deepseek-chat',  # 或 deepseek-coder
    'max_tokens': 1000,
    'temperature': 0.7,
}

# 兜底开关
AI_FALLBACK_ENABLED = True  # API失败时启用模板
```

### 2.2 核心服务类

```python
# services/ai_suggestion_service.py
import requests
from typing import Dict, Optional

class AISuggestionService:
    """AI建议生成服务"""
    
    def __init__(self):
        self.api_key = settings.DEEPSEEK_CONFIG['api_key']
        self.api_base = settings.DEEPSEEK_CONFIG['api_base']
        self.model = settings.DEEPSEEK_CONFIG['model']
        self.fallback = FallbackTemplateService()
    
    def generate_counselor_suggestion(self, student_data: Dict) -> Dict:
        """
        为辅导员生成干预建议
        
        Args:
            student_data: {
                'name': '张三',
                'warning_level': '红色预警',
                'avg_score': 48,
                'weak_courses': ['数据结构', '高等数学'],
                'absence_count': 8,
                'homework_rate': '45%',
                'video_progress': '30%'
            }
        
        Returns:
            {
                'analysis': '问题分析文本',
                'suggestions': ['建议1', '建议2', ...],
                'parent_script': '家长沟通话术',
                'encouragement_letter': '学生激励信',
                'source': 'ai' | 'template'
            }
        """
        try:
            result = self._call_deepseek_api(
                prompt=self._build_counselor_prompt(student_data),
                student_data=student_data
            )
            result['source'] = 'ai'
            return result
        except Exception as e:
            # API失败，使用模板兜底
            if settings.AI_FALLBACK_ENABLED:
                return self.fallback.get_counselor_suggestion(student_data)
            raise e
    
    def generate_teacher_suggestion(self, course_data: Dict, student_data: Optional[Dict] = None) -> Dict:
        """为教师生成教学建议"""
        try:
            if student_data:
                # 单个学生评语
                prompt = self._build_teacher_student_prompt(course_data, student_data)
            else:
                # 全班课程分析
                prompt = self._build_teacher_course_prompt(course_data)
            
            result = self._call_deepseek_api(prompt, course_data)
            result['source'] = 'ai'
            return result
        except Exception:
            if settings.AI_FALLBACK_ENABLED:
                return self.fallback.get_teacher_suggestion(course_data, student_data)
            raise
    
    def _call_deepseek_api(self, prompt: str, context_data: Dict) -> Dict:
        """调用DeepSeek API"""
        response = requests.post(
            f"{self.api_base}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "你是一位专业的大学学业辅导专家..."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            },
            timeout=10  # 10秒超时
        )
        response.raise_for_status()
        
        # 解析返回内容
        content = response.json()['choices'][0]['message']['content']
        return self._parse_ai_response(content)
    
    def _build_counselor_prompt(self, data: Dict) -> str:
        """构建辅导员场景Prompt"""
        return f"""你是一位有10年经验的大学辅导员，擅长学生学业预警干预。

学生情况：
- 姓名：{data['name']}
- 预警等级：{data['warning_level']}
- 当前平均成绩：{data['avg_score']}分
- 薄弱科目：{', '.join(data['weak_courses'])}
- 缺勤次数：{data['absence_count']}次
- 作业完成率：{data['homework_rate']}
- 视频学习进度：{data['video_progress']}

请按以下JSON格式返回：
{{
    "analysis": "对该学生问题的简要分析（2-3句话）",
    "suggestions": ["具体可执行的干预建议1", "建议2", "建议3"],
    "parent_script": "给家长的沟通文案，语气正式但有温度，100字左右",
    "encouragement_letter": "给学生的激励信，鼓励为主，指出问题但不过度批评，150字左右"
}}"""
```

### 2.3 模板兜底服务

```python
# services/fallback_template_service.py

class FallbackTemplateService:
    """模板兜底服务 - API失败时使用"""
    
    TEMPLATES = {
        'red_warning': {
            'analysis': "{name}同学当前学业风险极高，平均成绩{avg_score}分，{absence_count}次缺勤，作业完成率仅{homework_rate}，需要立即干预。",
            'suggestions': [
                "立即约谈学生，了解是否存在学习困难或生活问题",
                "联系家长通报情况，寻求家庭支持配合",
                "安排学习帮扶小组或推荐一对一辅导",
                "建议学生调整时间管理，减少非必要活动"
            ],
            'parent_script': "您好，我是{name}的辅导员。孩子本学期学业出现较大困难，多门课程成绩不理想，缺勤较多。想跟您沟通一下，看家里是否了解相关情况，希望能一起帮助孩子渡过难关。",
            'encouragement_letter': "{name}同学你好，老师注意到你最近在学习上遇到了一些困难。不要灰心，很多学长学姐也曾面临类似挑战。建议你主动找老师聊聊，制定一个循序渐进的学习计划。相信只要你愿意改变，一定能迎头赶上！"
        },
        'orange_warning': {
            'analysis': "{name}同学存在明显学业风险，{weak_courses}等科目薄弱，需要及时关注和干预。",
            'suggestions': [
                "约谈了解学习困难原因",
                "推荐参加薄弱科目的补习班",
                "建立定期学习反馈机制"
            ],
            'parent_script': "您好，{name}这学期在{weak_courses}等科目上有些吃力，我们希望一起关注下孩子的学习状态。",
            'encouragement_letter': "{name}同学，老师发现你在{weak_courses}上需要多花些功夫。有问题及时向老师同学请教，不要积压疑问。加油！"
        },
        'yellow_warning': {
            'analysis': "{name}同学学习态度需要改善，存在下滑趋势，建议适当提醒。",
            'suggestions': [
                "非正式谈话了解情况",
                "提醒注意学习节奏"
            ],
            'parent_script': "您好，想跟您说一下{name}最近的学习情况，建议家里也多关注下。",
            'encouragement_letter': "{name}同学，学习需要持之以恒，老师相信你能做得更好！"
        }
    }
    
    def get_counselor_suggestion(self, student_data: Dict) -> Dict:
        """获取辅导员建议（模板版）"""
        level = student_data['warning_level']
        template_key = self._map_warning_level(level)
        template = self.TEMPLATES[template_key]
        
        # 填充变量
        return {
            'analysis': template['analysis'].format(**student_data),
            'suggestions': template['suggestions'],
            'parent_script': template['parent_script'].format(**student_data),
            'encouragement_letter': template['encouragement_letter'].format(**student_data),
            'source': 'template',
            'note': '当前使用预设模板，AI服务恢复后将提供更个性化建议'
        }
    
    def _map_warning_level(self, level: str) -> str:
        mapping = {
            '红色预警': 'red_warning',
            '橙色预警': 'orange_warning',
            '黄色预警': 'yellow_warning'
        }
        return mapping.get(level, 'yellow_warning')
```

---

## 3. 前端界面设计

### 3.1 辅导员端 - AI建议生成弹窗

```vue
<!-- CounselorAISuggestion.vue -->
<template>
  <el-dialog v-model="visible" title="AI智能建议" width="700px">
    <div class="ai-suggestion-dialog">
      <!-- 生成类型选择 -->
      <div class="type-selector">
        <el-radio-group v-model="suggestionType">
          <el-radio-button label="counselor">辅导员参考</el-radio-button>
          <el-radio-button label="parent">家长沟通文案</el-radio-button>
          <el-radio-button label="student">学生激励信</el-radio-button>
        </el-radio-group>
        <el-button type="primary" :loading="generating" @click="generate">
          <el-icon><Magic /></el-icon>
          生成建议
        </el-button>
      </div>
      
      <!-- 生成结果 -->
      <div v-if="result" class="result-box">
        <el-alert 
          v-if="result.source === 'template'" 
          type="info" 
          :closable="false"
          show-icon
        >
          当前使用预设模板生成，AI服务恢复后将提供更个性化建议
        </el-alert>
        
        <!-- 辅导员参考 -->
        <template v-if="suggestionType === 'counselor'">
          <div class="section">
            <h4>问题分析</h4>
            <p>{{ result.analysis }}</p>
          </div>
          <div class="section">
            <h4>干预建议</h4>
            <ol>
              <li v-for="(item, i) in result.suggestions" :key="i">{{ item }}</li>
            </ol>
          </div>
        </template>
        
        <!-- 家长沟通/学生激励 -->
        <template v-else>
          <div class="section">
            <h4>{{ suggestionType === 'parent' ? '家长沟通文案' : '学生激励信' }}</h4>
            <el-input 
              v-model="resultText" 
              type="textarea" 
              :rows="6"
              resize="none"
            />
          </div>
        </template>
        
        <!-- 操作按钮 -->
        <div class="actions">
          <el-button @click="copy">复制内容</el-button>
          <el-button @click="regenerate">重新生成</el-button>
          <el-button type="primary" @click="saveToRecord">保存到干预记录</el-button>
        </div>
      </div>
      
      <!-- 空状态 -->
      <el-empty v-else description="点击"生成建议"获取AI分析" />
    </div>
  </el-dialog>
</template>
```

### 3.2 教师端 - AI辅助功能

```vue
<!-- TeacherAIFeatures.vue -->
<template>
  <div class="teacher-ai-features">
    <!-- 课程级AI分析 -->
    <el-card v-if="selectedCourse">
      <template #header>
        <div class="card-header">
          <span>AI课程分析</span>
          <el-button size="small" type="primary" @click="analyzeCourse">
            <el-icon><Magic /></el-icon>
            分析课程数据
          </el-button>
        </div>
      </template>
      <div v-if="courseAnalysis" class="analysis-content">
        <div class="analysis-item">
          <h4>薄弱知识点</h4>
          <p>{{ courseAnalysis.weak_points }}</p>
        </div>
        <div class="analysis-item">
          <h4>教学建议</h4>
          <ul>
            <li v-for="(tip, i) in courseAnalysis.suggestions" :key="i">{{ tip }}</li>
          </ul>
        </div>
      </div>
    </el-card>
    
    <!-- 学生评语生成 -->
    <el-card v-if="selectedStudent">
      <template #header>
        <div class="card-header">
          <span>AI评语生成 - {{ selectedStudent.name }}</span>
          <el-button size="small" @click="generateComment">
            生成评语
          </el-button>
        </div>
      </template>
      <el-input 
        v-if="studentComment" 
        v-model="studentComment" 
        type="textarea" 
        :rows="4"
      />
    </el-card>
  </div>
</template>
```

---

## 4. API接口设计

```yaml
# AI建议相关接口

POST /api/ai/counselor-suggestion
  body:
    student_id: string
    type: "full" | "parent" | "encouragement"
  response:
    analysis: string
    suggestions: [string]
    parent_script: string
    encouragement_letter: string
    source: "ai" | "template"

POST /api/ai/teacher-suggestion
  body:
    course_id: string
    student_id: string?  # 不传则分析全班
  response:
    weak_points: string
    suggestions: [string]
    student_comment: string  # 学生评语
    source: "ai" | "template"

GET /api/ai/status
  response:
    available: boolean  # AI服务是否可用
    fallback_enabled: boolean
```

---

## 5. 成本估算

### DeepSeek API费用
- 模型：deepseek-chat
- 价格：约 ¥2 / 百万token
- 单次请求约 500-800 token
- 估算：1000次请求 ≈ ¥1.6

### 使用限制（可选）
```python
# 每日请求限制，控制成本
DAILY_AI_QUOTA = {
    'counselor': 50,   # 辅导员每日50次
    'teacher': 30,     # 教师每日30次
}
```

---

## 6. 实施步骤

1. **申请DeepSeek API Key**（免费额度足够毕设使用）
2. **实现模板兜底服务**（不依赖API，可先完成）
3. **实现DeepSeek API服务**
4. **前端界面开发**
5. **联调测试**

---

## 7. 记录变更

| 时间 | 变更 | 说明 |
|------|------|------|
| 2026-04-05 | 创建文档 | 确定DeepSeek API + 模板兜底方案 |
