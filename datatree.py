import json
import os

import aiofiles
import asyncio

class DataTree:
	"""
	JSON style hierarchical data structure. Stores labels (strings) paired to data (either strings or other DataTrees). Automatically creates parent trees as needed, to avoid KeyErrors.
	"""
	def __init__(self, tree=None, parent=None):
		"""Initialize the DataTree, loading existing data if needed."""
		# Contains string-to-string and string-to-DataTree pairs.
		self.parent = parent
		self._tree = {} 
		if tree:
			for key, value in tree.items():
				self._tree[str(key)] = self._make_dt_compat(value)

	def _make_dt_compat(self, obj):
		"""Converts an object to either a DataTree or a string, depending on its' type."""
		return DataTree(obj, parent=self) if isinstance(obj, dict) else obj if isinstance(obj, DataTree) else str(obj)
	
	def __repr__(self):
		"""Returns a JSON-style representation of the DataTree."""
		return json.dumps(self.to_dict(), indent=4)
	
	def __getitem__(self, key):
		"""Get the value of DataTree[key]. Creates new parents if they do not exist yet (these do not get written to disk until actual data is changed elsewhere)."""
		key = str(key)
		if key not in self._tree:
			self._tree[key] = DataTree(parent=self)
		return self._make_dt_compat(self._tree[key])
	
	def __setitem__(self, key, value):
		"""Set DataTree[key] = value."""
		key = str(key)
		value = self._make_dt_compat(value)
		self._tree[key] = value
		asyncio.create_task(self._save())

	def __delitem__(self, key):
		"""Delete DataTree[key]."""
		key = str(key)
		del self._tree[key]
		asyncio.create_task(self._save())

	def __contains__(self, key):
		"""Check if DataTree[key] exists (current level only)."""
		return str(key) in self._tree

	def keys(self):
		"""Returns a list of all keys at the root of the DataTree."""
		return self._tree.keys()
	
	def is_empty(self):
		return not bool(len(self._tree))
	
	def _prune(self):
		"""Remove all sub-DataTrees which do not contain any items."""
		to_delete = []
		for key, value in list(self._tree.items()):
			if isinstance(value, DataTree):
				value._prune()
				if value.is_empty():
					to_delete.append(key)
		for key in to_delete:
			del self._tree[key]

	def to_dict(self):
		"""Return a dictionary that can be serialized."""
		out = {}
		for key, value in self._tree.items():
			if isinstance(value, DataTree):
				out[key] = value.to_dict()
			else:
				out[key] = value
		return out
	
	async def _save(self):
		"""This does not save to disk and is only implemented to allow for propagation."""
		if self.parent:
			await self.parent._save()
		

class SelfWritingDataTree(DataTree):
	"""
	A DataTree, except it pulls its' data from a file, and every time it is modified, it writes back to that file.
	"""
	def __init__(self, filename):
		"""Initialize the SelfWritingDataTree, loading existing data from a file."""
		self.filename = filename
		self._tree = {}
		self._load()

	def _load(self):
		"""Loads JSON data from self.filename to self._tree."""
		if os.path.exists(self.filename):
			with open(self.filename, mode='r') as f:
				dict_tree = json.load(f)
		else:
			dict_tree = {}
		self._tree = DataTree(dict_tree, parent=self)._tree
		
	async def _save(self):
		"""Asynchronously saves JSON data from self._tree to self.filename."""
		self._prune()
		async with aiofiles.open(self.filename, mode='w') as f:
			await f.write(str(self))
