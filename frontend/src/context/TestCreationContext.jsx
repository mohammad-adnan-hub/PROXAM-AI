import { createContext, useContext, useState, useEffect } from 'react'

const STORAGE_KEY = 'proxam_test_creation_draft'

const DEFAULT_DRAFT = {
  title: '',
  description: '',
  instructions: '',
  duration_minutes: 60,
  questions: [],
}

const TestCreationContext = createContext(null)

export function TestCreationProvider({ children }) {
  const [draft, setDraft] = useState(() => {
    try {
      const saved = sessionStorage.getItem(STORAGE_KEY)
      if (saved) {
        return JSON.parse(saved)
      }
    } catch {
      // ignore JSON parse or session storage errors
    }
    return DEFAULT_DRAFT
  })

  // Sync with session storage whenever draft changes
  useEffect(() => {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(draft))
    } catch {
      // ignore storage quota errors
    }
  }, [draft])

  const updateBasicInfo = ({ title, description, instructions, duration_minutes }) => {
    setDraft((prev) => ({
      ...prev,
      title: title !== undefined ? title : prev.title,
      description: description !== undefined ? description : prev.description,
      instructions: instructions !== undefined ? instructions : prev.instructions,
      duration_minutes:
        duration_minutes !== undefined ? Number(duration_minutes) : prev.duration_minutes,
    }))
  }

  const addQuestion = (question) => {
    setDraft((prev) => ({
      ...prev,
      questions: [
        ...prev.questions,
        {
          ...question,
          order_index: prev.questions.length,
        },
      ],
    }))
  }

  const updateQuestion = (index, updatedQuestion) => {
    setDraft((prev) => {
      const updated = [...prev.questions]
      updated[index] = {
        ...updatedQuestion,
        order_index: index,
      }
      return {
        ...prev,
        questions: updated,
      }
    })
  }

  const deleteQuestion = (index) => {
    setDraft((prev) => {
      const filtered = prev.questions
        .filter((_, i) => i !== index)
        .map((q, i) => ({ ...q, order_index: i }))
      return {
        ...prev,
        questions: filtered,
      }
    })
  }

  const reorderQuestions = (fromIndex, toIndex) => {
    setDraft((prev) => {
      if (
        fromIndex < 0 ||
        fromIndex >= prev.questions.length ||
        toIndex < 0 ||
        toIndex >= prev.questions.length
      ) {
        return prev
      }
      const list = [...prev.questions]
      const [moved] = list.splice(fromIndex, 1)
      list.splice(toIndex, 0, moved)
      return {
        ...prev,
        questions: list.map((q, i) => ({ ...q, order_index: i })),
      }
    })
  }

  const resetDraft = () => {
    setDraft(DEFAULT_DRAFT)
    try {
      sessionStorage.removeItem(STORAGE_KEY)
    } catch {
      // ignore
    }
  }

  const isBasicInfoValid = () => {
    return (
      Boolean(draft.title && draft.title.trim()) &&
      draft.duration_minutes >= 1 &&
      draft.duration_minutes <= 600
    )
  }

  const isQuestionsValid = () => {
    if (!draft.questions || draft.questions.length === 0) return false
    return draft.questions.every((q) => {
      if (!q.question_text || !q.question_text.trim()) return false
      if (!q.options || q.options.length !== 4) return false
      const allTextsFilled = q.options.every((opt) => opt.option_text && opt.option_text.trim())
      const correctCount = q.options.filter((opt) => opt.is_correct).length
      return allTextsFilled && correctCount === 1
    })
  }

  return (
    <TestCreationContext.Provider
      value={{
        draft,
        updateBasicInfo,
        addQuestion,
        updateQuestion,
        deleteQuestion,
        reorderQuestions,
        resetDraft,
        isBasicInfoValid,
        isQuestionsValid,
      }}
    >
      {children}
    </TestCreationContext.Provider>
  )
}

export function useTestCreation() {
  const context = useContext(TestCreationContext)
  if (!context) {
    throw new Error('useTestCreation must be used within a TestCreationProvider')
  }
  return context
}
