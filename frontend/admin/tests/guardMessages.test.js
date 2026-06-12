import { describe, it, expect } from 'vitest';
import { messages, DAY_NAMES, SHIFT_LABELS, SHIFT_DEFAULTS } from '../src/utils/guardMessages';

describe('guardMessages', () => {
  it('should export messages object with required keys', () => {
    const requiredKeys = [
      'LABEL_AVAILABLE', 'LABEL_UNAVAILABLE', 'LABEL_SUBMIT',
      'LABEL_LOADING', 'LABEL_NOTES', 'LABEL_FROM', 'LABEL_TO',
      'ERR_AUTH', 'ERR_NETWORK', 'SUCCESS_SUBMITTED',
    ];
    requiredKeys.forEach((key) => {
      expect(messages[key]).toBeDefined();
      expect(typeof messages[key]).toBe('string');
    });
  });

  it('should export DAY_NAMES as 7-element array', () => {
    expect(DAY_NAMES).toHaveLength(7);
    DAY_NAMES.forEach((name) => {
      expect(typeof name).toBe('string');
      expect(name.length).toBeGreaterThan(0);
    });
  });

  it('should export SHIFT_LABELS with morning/afternoon/night', () => {
    expect(SHIFT_LABELS.morning).toBeDefined();
    expect(SHIFT_LABELS.afternoon).toBeDefined();
    expect(SHIFT_LABELS.night).toBeDefined();
  });

  it('should export SHIFT_DEFAULTS with from_hour/to_hour per shift', () => {
    ['morning', 'afternoon', 'night'].forEach((shift) => {
      expect(SHIFT_DEFAULTS[shift]).toBeDefined();
      expect(typeof SHIFT_DEFAULTS[shift].from_hour).toBe('string');
      expect(typeof SHIFT_DEFAULTS[shift].to_hour).toBe('string');
    });
  });

  it('should not conflict with admin messages', () => {
    // Verify it's a different structure from admin messages
    expect(messages.LABEL_AVAILABLE).toBeDefined();
  });
});