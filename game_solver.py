# -*- coding: utf-8 -*-
from collections import deque

CHARS = ['A', 'B', 'C', 'D', 'E']
COLORS = ['red', 'blue', 'green', 'yellow', 'purple']
N = 5
MAX_ACTIONS = 31

STICK_LABEL  = "木槌"
BUCKET_LABEL = "颜料"
ACTION_NAME  = {0: "攻击 (attacks)", 1: "防御 (defends)"}


# ── Game logic ───────────────────────────────────────────────────────────────

def apply_action(sticks, buckets, char_idx, action):
    """
    Swap-based interpretation of 'passing':
    Attack  (action=0): swap stick with right+1, swap bucket with left+2
    Defend  (action=1): swap stick with right+2, swap bucket with left+1
    """
    sticks = list(sticks)
    buckets = list(buckets)
    i = char_idx

    if action == 0:  # attack
        right1 = (i + 1) % N
        left2  = (i + 3) % N
        sticks[i],  sticks[right1]  = sticks[right1],  sticks[i]
        buckets[i], buckets[left2]  = buckets[left2],  buckets[i]
    else:            # defend
        right2 = (i + 2) % N
        left1  = (i + 4) % N
        sticks[i],  sticks[right2]  = sticks[right2],  sticks[i]
        buckets[i], buckets[left1]  = buckets[left1],  buckets[i]

    return tuple(sticks), tuple(buckets)


def is_goal(sticks, buckets):
    return all(sticks[i] == buckets[i] for i in range(N))


def bfs(initial_sticks, initial_buckets):
    initial_state = (tuple(initial_sticks), tuple(initial_buckets))

    if is_goal(*initial_state):
        return []

    queue = deque([(initial_state, [])])
    visited = {initial_state}

    while queue:
        (sticks, buckets), path = queue.popleft()

        if len(path) >= MAX_ACTIONS:
            continue

        for char_idx in range(N):
            for action in range(2):
                new_sticks, new_buckets = apply_action(sticks, buckets, char_idx, action)
                new_state = (new_sticks, new_buckets)

                if new_state not in visited:
                    visited.add(new_state)
                    new_path = path + [(char_idx, action)]
                    if is_goal(new_sticks, new_buckets):
                        return new_path
                    queue.append((new_state, new_path))

    return None


# ── Input helpers ────────────────────────────────────────────────────────────

ABBREV = {c[0]: c for c in COLORS}   # r→red, b→blue, g→green, y→yellow, p→purple


def get_color_input(prompt, used=None):
    while True:
        raw = input(prompt).strip().lower()
        color = ABBREV.get(raw, raw)
        if color not in COLORS:
            print(f"      无效颜色。可选：{', '.join(COLORS)}（或首字母 r/b/g/y/p）")
        elif used is not None and color in used:
            print(f"      '{color}' 已被使用，请选择其他颜色。")
        else:
            return color


def input_character_names():
    """Ask once per game for the Chinese name of each character."""
    print()
    print("  请为五位角色输入中文名（每轮保持不变）：")
    names = {}
    for char in CHARS:
        name = input(f"    角色 {char} 的名字：").strip()
        if not name:
            name = char   # fall back to letter if left blank
        names[char] = name
    return names


def input_round_state(names):
    sticks, buckets = [], []
    used_sticks, used_buckets = set(), set()

    print(f"\n  颜色选项：{', '.join(COLORS)}")
    print("  （可输入完整颜色名或首字母：r/b/g/y/p）\n")

    for char in CHARS:
        label = f"{names[char]}（{char}）"
        print(f"  {label}：")
        s = get_color_input(f"    {STICK_LABEL} 颜色：", used_sticks)
        used_sticks.add(s)
        sticks.append(COLORS.index(s))

        b = get_color_input(f"    {BUCKET_LABEL} 颜色：", used_buckets)
        used_buckets.add(b)
        buckets.append(COLORS.index(b))
        print()

    return sticks, buckets


# ── Display helpers ──────────────────────────────────────────────────────────

def print_state(sticks, buckets, names, label="当前状态"):
    print(f"  {label}：")
    print(f"  {'角色':<8} {STICK_LABEL:<8} {BUCKET_LABEL:<8}")
    print("  " + "─" * 28)
    for i, char in enumerate(CHARS):
        name_label = f"{names[char]}({char})"
        match_mark = "  ✓" if sticks[i] == buckets[i] else ""
        print(f"  {name_label:<8} {COLORS[sticks[i]]:<8} {COLORS[buckets[i]]:<8}{match_mark}")


def print_solution(solution, initial_sticks, initial_buckets, names):
    if solution is None:
        print(f"\n  未能在 {MAX_ACTIONS} 步内找到解法。")
        print("  （此配置可能不是游戏中的合法初始状态。）")
        return

    if len(solution) == 0:
        print("\n  所有角色颜色已匹配，无需操作！")
        return

    print(f"\n  解法：共 {len(solution)} 步\n")
    print(f"  {'步骤':>4}  {'角色':<10}  动作")
    print("  " + "─" * 36)

    sticks  = list(initial_sticks)
    buckets = list(initial_buckets)

    for step, (char_idx, action) in enumerate(solution, 1):
        char = CHARS[char_idx]
        name_label = f"{names[char]}({char})"
        print(f"  {step:>4}.  {name_label:<10}  {ACTION_NAME[action]}")
        new_sticks, new_buckets = apply_action(
            tuple(sticks), tuple(buckets), char_idx, action
        )
        sticks, buckets = list(new_sticks), list(new_buckets)

    print()
    print_state(sticks, buckets, names, label="最终状态")


def ask_next_action():
    """Ask user whether to play another round, restart the game, or quit."""
    print()
    print("  请选择：")
    print("    r — 继续下一回合（保留角色名称）")
    print("    n — 重新开始（重新输入角色名称）")
    print("    q — 退出游戏")
    while True:
        choice = input("  你的选择（r/n/q）：").strip().lower()
        if choice in ("r", "n", "q"):
            return choice
        print("  请输入 r、n 或 q。")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print()
    print("=" * 52)
    print("    木槌 & 颜料 配色求解器")
    print("=" * 52)
    print(f"  角色排列：A – B – C – D – E（循环）")
    print(f"  攻击：{STICK_LABEL}→右+1，{BUCKET_LABEL}→左+2")
    print(f"  防御：{STICK_LABEL}→右+2，{BUCKET_LABEL}→左+1")
    print(f"  每轮上限：{MAX_ACTIONS} 步")

    names = input_character_names()

    while True:
        sticks, buckets = input_round_state(names)
        print_state(sticks, buckets, names, label="初始状态")

        print("\n  正在搜索最优解法…")
        solution = bfs(sticks, buckets)
        print_solution(solution, sticks, buckets, names)

        choice = ask_next_action()
        if choice == "q":
            break
        elif choice == "n":
            print()
            print("=" * 52)
            names = input_character_names()

    print("\n  游戏结束，再见！\n")


if __name__ == "__main__":
    main()
