import { createContext, useContext, useCallback, useRef, useState, type ReactNode } from 'react'
import { driver, type Driver } from 'driver.js'

const TOUR_SEEN_KEY = 'mizan_tour_seen'

interface TourContextValue {
  startTour: () => void
  tourSeen: boolean
}

const TourContext = createContext<TourContextValue>({
  startTour: () => {},
  tourSeen: true,
})

export function TourProvider({ children }: { children: ReactNode }) {
  const driverRef = useRef<Driver | null>(null)
  const [tourSeen, setTourSeen] = useState<boolean>(
    () => localStorage.getItem(TOUR_SEEN_KEY) === 'true'
  )

  const startTour = useCallback(() => {
    // Destroy any active instance before re-creating (prevents double-click bug)
    driverRef.current?.destroy()

    driverRef.current = driver({
      animate: true,
      overlayOpacity: 0.6,
      showProgress: true,
      progressText: '{{current}} / {{total}}',
      allowClose: true,
      allowKeyboardControl: true,
      nextBtnText: 'التالي ←',
      prevBtnText: '→ السابق',
      doneBtnText: 'ابدأ التدريب',
      popoverClass: 'mizan-tour-popover',
      steps: [
        {
          popover: {
            title: 'مرحباً بك في ميزان!',
            description: 'دعنا نعرّفك على المنصة في دقيقة واحدة.',
          },
        },
        {
          element: '#tour-logo',
          popover: {
            title: 'منصة ميزان',
            description: 'ميزان هي منصة للذكاء الاصطناعي لرصد خطاب الكراهية العربي وتدريب المشرفين.',
            side: 'bottom',
            align: 'start',
          },
        },
        {
          element: '#tour-nav',
          popover: {
            title: 'الأقسام الثلاثة',
            description: 'تنقّل بين المرصد ومدقق التحيز والتدريب من هذا الشريط.',
            side: 'bottom',
            align: 'start',
          },
        },
        {
          element: '#tour-card-observatory',
          popover: {
            title: 'المرصد — رانيا',
            description: 'هذا قسم رانيا — مسؤولة السياسات. تابعي اتجاهات خطاب الكراهية في الأردن على مدى ٨ سنوات.',
            side: 'bottom',
            align: 'start',
          },
        },
        {
          element: '#tour-card-audit',
          popover: {
            title: 'مدقق التحيز — لينا',
            description: 'هذا قسم لينا — باحثة NLP. قيّمي عدالة النموذج عبر فئات خطاب الكراهية التسع.',
            side: 'bottom',
            align: 'start',
          },
        },
        {
          element: '#tour-card-training',
          popover: {
            title: 'التدريب — خالد',
            description: 'هذا قسم خالد — مشرف المحتوى. ابدأ هنا! صنّف محتوى عربياً حقيقياً بمساعدة الذكاء الاصطناعي.',
            side: 'bottom',
            align: 'start',
          },
        },
      ],
      onDestroyed: () => {
        localStorage.setItem(TOUR_SEEN_KEY, 'true')
        setTourSeen(true)
      },
    })

    driverRef.current.drive()
  }, [])

  return (
    <TourContext.Provider value={{ startTour, tourSeen }}>
      {children}
    </TourContext.Provider>
  )
}

export function useTour() {
  return useContext(TourContext)
}

export function isTourSeen(): boolean {
  return localStorage.getItem(TOUR_SEEN_KEY) === 'true'
}
