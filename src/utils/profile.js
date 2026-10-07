/**
 * Checks if an authenticated user's profile and initial skills are complete.
 * Required fields: full_name, college, branch, year, at least 1 offered skill, at least 1 wanted skill.
 */
export function isProfileComplete(profile, offeredSkills = [], wantedSkills = []) {
  if (!profile) return false;

  const hasName = Boolean(profile.full_name && profile.full_name.trim());
  const hasCollege = Boolean(profile.college && profile.college.trim());
  const hasBranch = Boolean(profile.branch && profile.branch.trim());
  const hasYear = Boolean(profile.year);

  const hasOffered = Array.isArray(offeredSkills) && offeredSkills.length > 0;
  const hasWanted = Array.isArray(wantedSkills) && wantedSkills.length > 0;

  return hasName && hasCollege && hasBranch && hasYear && hasOffered && hasWanted;
}
