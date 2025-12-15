import service from './axios'

/**
 * Get AI sidebar prompt suggestions by route and language.
 * @param {Object} params
 * @param {string} params.route - current route path, e.g., "/alerts"
 * @param {string} params.lang - language code, "zh" | "en"
 */
export const getAIPrompts = ({ route, lang }) => {
  return service.get('/ai/prompt', {
    params: { route, lang }
  })
}

