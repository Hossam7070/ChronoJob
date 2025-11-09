import { AlertCircle, CheckCircle, Info, XCircle } from 'lucide-react'

interface AlertProps {
  type: 'success' | 'error' | 'warning' | 'info'
  title?: string
  message: string
  onClose?: () => void
}

const Alert = ({ type, title, message, onClose }: AlertProps) => {
  const config = {
    success: {
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      iconColor: 'text-green-400',
      textColor: 'text-green-800',
      titleColor: 'text-green-800',
      Icon: CheckCircle,
    },
    error: {
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      iconColor: 'text-red-400',
      textColor: 'text-red-700',
      titleColor: 'text-red-800',
      Icon: AlertCircle,
    },
    warning: {
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      iconColor: 'text-yellow-400',
      textColor: 'text-yellow-700',
      titleColor: 'text-yellow-800',
      Icon: AlertCircle,
    },
    info: {
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      iconColor: 'text-blue-400',
      textColor: 'text-blue-700',
      titleColor: 'text-blue-800',
      Icon: Info,
    },
  }

  const { bgColor, borderColor, iconColor, textColor, titleColor, Icon } = config[type]

  return (
    <div className={`${bgColor} border ${borderColor} rounded-md p-4`}>
      <div className="flex">
        <Icon className={`h-5 w-5 ${iconColor}`} />
        <div className="ml-3 flex-1">
          {title && <h3 className={`text-sm font-medium ${titleColor}`}>{title}</h3>}
          <p className={`${title ? 'mt-1' : ''} text-sm ${textColor}`}>{message}</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className={`ml-3 ${textColor} hover:opacity-75`}
          >
            <XCircle className="h-5 w-5" />
          </button>
        )}
      </div>
    </div>
  )
}

export default Alert
